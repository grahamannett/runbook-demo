from datetime import datetime
from typing import Sequence

import reflex as rx
from together import Together

from runbook_app import rag_tools
from runbook_app.db_models import ChatInteraction, Document, Runbook
from runbook_app.db_ops import (
    check_chat_interaction_exists,
    create_new_runbook,
    fetch_messages,
    get_runbook_chat_interactions,
    get_runbooks,
    save_chat_interaction,
)
from runbook_app.llm_tools import LLMConfig, create_messages_for_chat_completion, get_ai_client, get_ai_model
from runbook_app.utils import proc_ctx
from rxconstants import INPUT_BOX_ID, SCROLL_DOWN_ON_LOAD, rag_docs_storage_type, tz


class ChatState(rx.State):
    """The app state."""

    valid_session: bool = False

    filter_str: str = ""

    _ai_client_instance: Together | None = None
    _ai_chat_instance = None

    _input_box_id: str = INPUT_BOX_ID  # issue with reflex when this isnt a backend var

    has_checked_database: bool = False
    stream_resp: bool = True

    runbook_id: int | None = None
    runbooks: list[Runbook] = []
    chat_interactions: list[ChatInteraction] = []
    documents: list[Document]
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
            print("possibly was still processing document...")
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

    def handle_logout(self):
        print("logging out...")
        self.valid_session = False

    def handle_login_form(self, form_data: dict):
        print(f"data: {form_data}")
        self.valid_session = True
        return rx.redirect("/")

    def load_all_documents(self) -> None:
        # print(f"loading all documents...: {self.documents=}")
        self.documents = rag_tools.load_all_documents()
        print(f"loaded {len(self.documents)} documents")
        for doc in self.documents:
            print(f"{doc=}")

    def print_ai_info(self) -> None:
        print(f"{self.ai_provider=} | {self.ai_provider_url=} | {self.ai_provider_api_key=} | {self.ai_model=}")

    def _get_client_instance(self) -> Together:
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
        print("creating new runbook...")
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

    async def _process_response(self, resp):
        """Process the response from the chat completion, handling both streaming and non-streaming cases.

        Args:
            resp: The response from the chat completion session
        """
        if self.stream_resp:
            try:
                for item in resp:
                    if item.choices and item.choices[0] and item.choices[0].delta:
                        answer_text = item.choices[0].delta.content
                        # Ensure answer_text is not None before concatenation
                        if answer_text is not None:
                            self.chat_interactions[-1].answer += answer_text
                        else:
                            answer_text = ""
                            self.chat_interactions[-1].answer += answer_text

                        # this makes it so that we scroll while the response is being generated
                        yield rx.scroll_to(elem_id=self._input_box_id)

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
    def timestamp_formatted(self) -> str:
        return self.timestamp.strftime("%I:%M %p")

    # ----
    # ---- rx.Events
    # ----

    @rx.event(background=True)
    async def submit_prompt(self):
        async def _fetch_chat_completion_session(
            prompt: str,
        ):
            messages = create_messages_for_chat_completion(self.chat_interactions, prompt)
            client_instance: Together = self._get_client_instance()
            resp = client_instance.chat.completions.create(
                model=self.ai_model,
                messages=messages,
                max_tokens=512,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["<|eot_id|>", "<|eom_id|>"],
                truncate=130560,
                stream=self.stream_resp,
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
        # if not self.valid_session:
        #     return
        yield rx.scroll_to(elem_id=ChatState._input_box_id)

    @rx.event(background=True)
    async def add_document(self, form_data: dict = {}):
        print(f"adding document: {form_data=}")
        url = form_data.get("url", None)

        def btn_loading():
            self.processing_document = not self.processing_document

        async with proc_ctx(self, with_fn=(btn_loading,)) as self:
            yield rx.toast.info("Adding document...")
            if not rag_tools.valid_url(url):
                yield rx.toast.error("Invalid URL")
                return
            print(f"adding document to rag_document type: {rag_docs_storage_type}")
            yield rx.toast.success("added document")
