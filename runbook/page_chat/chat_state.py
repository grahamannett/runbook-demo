from datetime import datetime
from typing import Sequence

import reflex as rx
from reflex.utils import console

from runbook import rag_tools
from runbook.db_models import (
    ChatInteraction,
    DocumentSource,
    DocumentTableLookup,
    Runbook,
)
from runbook.db_ops import (
    check_chat_interaction_exists,
    create_new_runbook,
    fetch_messages,
    get_runbook_chat_interactions,
    get_runbooks,
    save_chat_interaction,
)
from runbook.llm_tools import (
    LLMClient,
    LLMConfig,
    ResponseType,
    create_html_parse_prompt,
    create_messages_for_chat_completion,
    get_ai_client,
    get_ai_model,
)
from runbook.utils import is_dev_mode, proc_ctx
from rxconstants import INPUT_BOX_ID, SCROLL_DOWN_ON_LOAD, app_password, tz


class ChatState(rx.State):
    """The app state."""

    valid_session: bool = False

    filter_str: str = ""
    document_markdown: str = ""

    _ai_client_instance: LLMClient | None = None

    has_checked_database: bool = False
    stream_resp: bool = True

    runbook_id: int | None = None
    runbooks: list[Runbook] = []
    chat_interactions: list[ChatInteraction] = []

    document_sources: list[DocumentSource] = []  # List of all HTML sources
    # documents: dict[int, Document] = {}  # Maps DocumentSource.id to Document if it exists
    processing_document: bool = False

    username: str = "user"
    prompt: str = ""
    result: str = ""
    ai_loading: bool = False
    timestamp: datetime = datetime.now(tz=tz)

    ai_provider: str = LLMConfig.ai_provider
    ai_provider_url: str = LLMConfig.ai_provider_url
    ai_provider_api_key: str = LLMConfig.ai_provider_api_key
    ai_model: str = LLMConfig.ai_model

    async def on_load_index(self):
        if self.processing_document:
            console.info("possibly was still processing document...")
            self.processing_document = False

        with rx.session() as session:
            self.runbooks = get_runbooks(username=self.username, session=session)

        if len(self.runbooks) <= 0:
            self.create_new_runbook()
        else:
            self.runbook_id = self.runbooks[0].id
            self.chat_interactions = get_runbook_chat_interactions(runbook_id=self.runbook_id, session=session)

        self.load_all_documents()

        # scroll to bottom - can maybe comment out
        if SCROLL_DOWN_ON_LOAD:
            yield ChatState.background_scroll_bottom_on_load()

    def check_document_parsed(self, doc_id: int) -> bool:
        print(f"checking documents: {self.documents}")
        if doc_id in self.documents:
            return True
        return False

    def handle_logout(self):
        console.info("logging out...")
        self.valid_session = False

    def view_document(self, doc_markdown: str):
        print(f"got markdown: {doc_markdown}")
        self.document_markdown = doc_markdown
        return rx.redirect("/document")

    def handle_login_form(self, form_data: dict):
        console.info(f"data: {form_data}")

        if form_data.get("app_password") == app_password:
            self.valid_session = True
            return rx.redirect("/")

    def load_all_documents(self) -> None:
        with rx.session() as session:
            # Only fetch non-deleted sources
            query = DocumentSource.select().where(DocumentSource.is_deleted == False)

            results = session.exec(query).all()
            self.document_sources = list(results)
            print(f"document sources: {self.document_sources}")

    def print_ai_info(self) -> None:
        console.info(f"{self.ai_provider=} | {self.ai_provider_url=} | {self.ai_provider_api_key=} | {self.ai_model=}")

    def _get_client_instance(self) -> LLMClient:
        if self._ai_client_instance is not None:
            return self._ai_client_instance

        if ai_client_instance := get_ai_client(
            ai_provider=self.ai_provider,
            ai_provider_url=self.ai_provider_url,
            ai_provider_api_key=self.ai_provider_api_key,
        ):
            self.ai_model = get_ai_model(ai_provider=self.ai_provider)
            self._ai_client_instance = ai_client_instance
            return ai_client_instance

        raise ValueError("AI client not found")

    def _fetch_messages(self) -> Sequence[ChatInteraction]:
        return fetch_messages(username=self.username, prompt=self.prompt)

    def set_prompt(self, prompt: str) -> None:
        self.prompt = prompt

    def create_new_runbook(self) -> None:
        # Create new runbook interaction,
        with rx.session() as session:
            _ = create_new_runbook(username=self.username, session=session)
            self.runbooks = get_runbooks(username=self.username, session=session)
            self.runbook_id = self.runbooks[0].id
            self.chat_interactions = get_runbook_chat_interactions(runbook_id=self.runbook_id, session=session)

    def _save_resulting_chat_interaction(self, chat_interaction: ChatInteraction) -> None:
        with rx.session() as session:
            save_chat_interaction(chat_interaction, session=session)

    def _check_saved_chat_interactions(self, username: str, prompt: str) -> bool:
        with rx.session() as session:
            return check_chat_interaction_exists(
                username=username,
                prompt=prompt,
                runbook_id=self.runbook_id,
                session=session,
            )

    async def _process_response(self, resp, response_type: ResponseType):
        if response_type == ResponseType.STREAM:
            try:
                for item in resp:
                    answer_text = stream_get_content_openai_api(item)
                    if answer_text is None:
                        answer_text = ""
                    self.chat_interactions[-1].answer += answer_text

                    # Scroll while the response is being generated
                    yield rx.scroll_to(elem_id=INPUT_BOX_ID)

            except StopAsyncIteration:
                raise

            self.result = self.chat_interactions[-1].answer

        else:
            self.chat_interactions[-1].answer = resp.choices[0].message.content
            self.result = self.chat_interactions[-1].answer

    # ----
    # ---- rx.Vars
    # ----

    @rx.var
    def send_message_text(self) -> str:
        if len(self.chat_interactions) == 0:
            return "Generate a runbook"
        return "Send Message"

    @rx.var
    def timestamp_formatted(self) -> str:
        return self.timestamp.strftime("%I:%M %p")

    @rx.var
    def len_documents(self) -> int:
        return len(self.document_sources)

    # @rx.var
    # d

    # ----
    # ---- rx.Events
    # ----

    @rx.event(background=True)
    async def regenerate_parsed_document(self, doc_id: int) -> None:
        with rx.session() as session:
            if not (doc := session.get(DocumentSource, ident=doc_id)):
                yield rx.toast.error("Document not found")
                return

            yield rx.toast.info(f"regenerating parsed document: {doc.path}")

        print(f"should still have doc: {doc.path}")
        async with self:
            client = get_ai_client(
                ai_provider=self.ai_provider,
                ai_provider_url=self.ai_provider_url,
                ai_provider_api_key=self.ai_provider_api_key,
            )
            model = self.ai_model

            # client_instance: LLMClient = self._get_client_instance()
        gen_kwargs = LLMConfig.ai_model_chat_completion_kwargs

        if "max_tokens" in gen_kwargs:
            _max_tokens = gen_kwargs.pop("max_tokens")

        print(f"chat completion kwargs: {gen_kwargs} | {len(doc.content)}")

        messages = create_html_parse_prompt(html_content=doc.content)
        resp = client.chat_completion(
            model=model,
            messages=messages,
            stream=False,
            temperature=0.5,
        )

        breakpoint()
        # resp = client_instance.chat_completion(model=self.ai_model, messages=messages, stream=False)
        # print

        # chat_kwargs = LLMConfig.ai_model_chat_completion_kwargs
        #     resp = client_instance.chat_completion(
        #         model=self.ai_model,
        #         messages=messages,
        #         stream=self.stream_resp,
        #         **chat_kwargs,
        #     )
        # messages = create_html_parse_prompt(html_content=)

    @rx.event(background=True)
    async def submit_prompt(self):
        async def _fetch_chat_completion_session(
            prompt: str,
            response_type: ResponseType,
        ):
            messages = create_messages_for_chat_completion(self.chat_interactions, prompt)

    @rx.event(background=True)
    async def submit_prompt(self):
        async def _fetch_chat_completion_session(
            prompt: str,
        ):
            messages = create_messages_for_chat_completion(self.chat_interactions, prompt)
            client_instance: LLMClient = self._get_client_instance()
            chat_kwargs = LLMConfig.ai_model_chat_completion_kwargs
            resp = client_instance.chat_completion(
                model=self.ai_model,
                messages=messages,
                stream=self.stream_resp,
                **chat_kwargs,
            )
            if resp is None:
                raise Exception("Session is None")

            return resp

        def set_ui_loading_state() -> None:
            self.ai_loading = True

        def clear_ui_loading_state() -> None:
            self.result = ""
            self.ai_loading = False

        def add_new_chat_interaction() -> None:
            self.chat_interactions.append(
                ChatInteraction(
                    prompt=prompt,
                    answer="",
                    chat_participant_user_name=self.username,
                    interaction_id=self.runbook_id,
                ),
            )
            self.prompt = ""

        # Get the question from the form
        if self.prompt == "":
            return

        prompt = self.prompt
        if self.username == "":
            raise ValueError("Username is required")

        if self._check_saved_chat_interactions(prompt=prompt, username=self.username):
            yield rx.toast.error("Question for this runbook already exists.")
            return

        async with self:
            set_ui_loading_state()
            yield

            resp = await _fetch_chat_completion_session(prompt)
            clear_ui_loading_state()
            add_new_chat_interaction()
            yield

            async for scroll_event in self._process_response(resp):
                yield scroll_event

        self._save_resulting_chat_interaction(chat_interaction=self.chat_interactions[-1])

    @rx.event(background=True)
    async def background_scroll_bottom_on_load(self):
        if self.valid_session or is_dev_mode():
            yield rx.scroll_to(elem_id=INPUT_BOX_ID)

    @rx.event(background=True)
    async def add_document(self, form_data: dict = {}):
        url = form_data.get("url", None)
        if not url:
            return

        def btn_loading():
            self.processing_document = not self.processing_document

        async with proc_ctx(self, hooks=(btn_loading,)) as self:
            with rx.session() as session:
                if not rag_tools.valid_url(url):
                    yield rx.toast.error("Invalid URL")
                    return

                if rag_tools.document_exists(url, session=session):
                    yield rx.toast.error("Document already fetched.")
                    return

                html_src = rag_tools.get_source(url)
                session.add(html_src)
                session.commit()
                session.refresh(html_src)

                yield rx.toast.success("added document")
                self.load_all_documents()

    @rx.event
    def delete_doc(self, doc_id: int, doc_table: str = "DocumentSource") -> None:
        entity = DocumentTableLookup[doc_table.lower()]

        with rx.session() as session:
            if doc := session.get(entity, doc_id):
                console.info(f"deleting: {doc=}")
                doc.is_deleted = True
                doc.deleted_at = datetime.now(tz=tz)
                session.commit()
                self.load_all_documents()
            else:
                console.info(f"doc not found: {doc_id=} | {doc_table=}")
