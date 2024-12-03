import functools
import os
from datetime import datetime
from typing import Sequence

import reflex as rx
from sqlalchemy import select
from together import Together

from runbook_app.components.auth_signin import signin
from runbook_app.db_models import ChatInteraction, Document, Runbook
from runbook_app.db_ops import (
    create_new_runbook,
    fetch_messages,
    get_runbook_chat_interactions,
    get_runbooks,
)
from runbook_app.dev_utils import is_dev_mode
from runbook_app.llm_tools import LLMConfig, create_messages_for_chat_completion, get_ai_client, get_ai_model
from rxconstants import tz

MAX_QUESTIONS = 10
INPUT_BOX_ID = "input-box"


def require_login(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    if is_dev_mode():
        return page

    @functools.wraps(page)
    def protected_page() -> rx.Component:
        return rx.box(
            rx.cond(
                AuthState.is_hydrated,
                rx.cond(AuthState.valid_session, page(), signin(on_submit_signin=AuthState.handle_submit)),
                rx.spinner(),
            ),
        )

    return protected_page


class AuthState(rx.State):
    valid_session: bool = False

    def handle_submit(self, form_data: dict):
        print(f"data: {form_data}")
        self.valid_session = True
        return rx.redirect("/")

    def logout(self):
        self.valid_session = False
        return rx.redirect("/")


class ChatState(rx.State):
    """The app state."""

    filter_str: str = ""

    _ai_client_instance: Together | None = None
    _ai_model: str | None = None
    _ai_chat_instance = None

    has_checked_database: bool = False
    stream_resp: bool = True

    runbook_id: int | None = None
    runbooks: list[Runbook] = []
    chat_interactions: list[ChatInteraction] = []
    documents: list[Document]

    has_token: bool = True
    username: str = "user"
    prompt: str = ""
    result: str = ""
    ai_loading: bool = False
    timestamp: datetime = datetime.now(tz=tz)

    ai_provider: str = LLMConfig.ai_provider
    ai_provider_url: str = LLMConfig.ai_provider_url
    ai_provider_api_key: str = LLMConfig.ai_provider_api_key

    @rx.var
    def timestamp_formatted(
        self,
    ) -> str:
        return self.timestamp.strftime("%I:%M %p")

    def load_all_documents(self) -> None:
        print("loading all documents...")

    def processes_url(self, data: dict) -> None:
        print(f"processing url: {data}")

    def print_ai_info(self) -> None:
        print(f"AI_PROVIDER: {self.ai_provider}")
        print(f"AI_PROVIDER_URL: {self.ai_provider_url}")
        print(f"AI_PROVIDER_API_KEY: {self.ai_provider_api_key}")

    def _get_client_instance(
        self,
    ) -> Together:
        if self._ai_client_instance is not None:
            return self._ai_client_instance

        if ai_client_instance := get_ai_client(
            ai_provider=self.ai_provider,
            ai_provider_url=self.ai_provider_url,
            ai_provider_api_key=self.ai_provider_api_key,
        ):
            self._ai_client_instance = ai_client_instance
            self._ai_model = get_ai_model(ai_provider=self.ai_provider)
            return ai_client_instance

        raise ValueError("AI client not found")

    def _fetch_messages(self) -> Sequence[ChatInteraction]:
        return fetch_messages(username=self.username, prompt=self.prompt)

    def on_load_index(self) -> None:
        self.runbooks = list(get_runbooks(username=self.username))
        if len(self.runbooks) <= 0:
            self.runbooks = [create_new_runbook(username=self.username)]

        if self.runbook_id is None:
            self.runbook_id = self.runbooks[0].id

        self.chat_interactions = get_runbook_chat_interactions(runbook_id=self.runbook_id)

    def get_html_document(self, url: str) -> None:
        # Create directory if it doesn't exist
        os.makedirs("runbook-documents", exist_ok=True)

    def set_prompt(
        self,
        prompt: str,
    ) -> None:
        self.prompt = prompt

    def create_new_chat(
        self,
    ) -> None:
        pass

    def _save_resulting_chat_interaction(
        self,
        chat_interaction: ChatInteraction,
    ) -> None:
        with rx.session() as session:
            session.add(
                chat_interaction,
            )
            session.commit()
            session.refresh(chat_interaction)

    def _check_saved_chat_interactions(self, username: str, prompt: str) -> bool:
        with rx.session() as session:
            query = (
                select(ChatInteraction)
                .where(
                    ChatInteraction.chat_participant_user_name == username,
                )
                .where(
                    ChatInteraction.prompt == prompt,
                )
                .where(
                    ChatInteraction.interaction_id == self.runbook_id,
                )
            )

            asked_previously = session.exec(query)

            asked_previously = asked_previously.scalar_one_or_none()
            return asked_previously is not None

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

                        yield rx.scroll_to(
                            elem_id=INPUT_BOX_ID,
                        )

            except StopAsyncIteration:
                raise

            self.result = self.chat_interactions[-1].answer

        else:
            self.chat_interactions[-1].answer = resp.choices[0].message.content
            self.result = self.chat_interactions[-1].answer

    @rx.event(background=True)
    async def submit_prompt(
        self,
    ):
        async def _fetch_chat_completion_session(
            prompt: str,
        ):
            messages = create_messages_for_chat_completion(self.chat_interactions, prompt)
            client_instance: Together = self._get_client_instance()
            resp = client_instance.chat.completions.create(
                model=self._ai_model,
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

        if prev_exists := self._check_saved_chat_interactions(
            prompt=prompt,
            username=self.username,
        ):
            yield rx.toast.error(
                "You have already asked this question or have asked too many questions in the past 24 hours.",
            )
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
