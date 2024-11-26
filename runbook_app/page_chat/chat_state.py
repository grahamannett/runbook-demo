from __future__ import annotations

import datetime
import os
import zoneinfo

import reflex as rx

# Import open-telemetry dependencies
from sqlalchemy import or_, select
from together import Together

from .chat_messages.model_chat_interaction import ChatInteraction

AI_MODEL: str = "UNKNOWN"
OTEL_HEADERS: str | None = None
OTEL_ENDPOINT: str | None = None
RUN_WITH_OTEL: bool = False


def get_ai_client() -> Together:
    ai_provider = os.environ.get("AI_PROVIDER")
    match ai_provider:
        case "ollama":
            return Together(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
            )

        case "together":
            return Together(
                api_key=os.environ.get("TOGETHER_API_KEY"),
            )
        case "openai":
            raise NotImplementedError("Only using Ollama/Together for now")

        case _:
            print("Invalid AI provider, please set AI_PROVIDER environment variable")


def get_ai_model() -> None:
    global AI_MODEL
    ai_model = os.environ.get("AI_PROVIDER")
    match ai_model:
        case "ollama":
            AI_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2-vision:11b")
        case "openai":
            raise NotImplementedError("Only using Ollama/Together for now")
        case "together":
            AI_MODEL = "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"

        case _:
            print("Invalid AI provider. Please set AI_PROVIDER environment variable")


model_name = get_ai_model()


# Set the tracer provider

MAX_QUESTIONS = 10
INPUT_BOX_ID = "input-box"

class AuthState(rx.State):
    allowed: bool = False



class ChatState(rx.State):
    """The app state."""

    filter: str = ""

    _ai_client_instance: Together | None = None
    _ai_chat_instance = None

    has_checked_database: bool = False

    chat_interactions: list[ChatInteraction] = []

    has_token: bool = True
    username: str = "Mauro Sicard"
    prompt: str = ""
    result: str = ""
    ai_loading: bool = False
    timestamp: datetime.datetime = datetime.datetime.now(
        tz=zoneinfo.ZoneInfo("America/Boise"),
    )

    @rx.var
    def timestamp_formatted(
        self,
    ) -> str:
        return self.timestamp.strftime("%I:%M %p")

    def _get_client_instance(
        self,
    ) -> Together:
        if self._ai_client_instance is not None:
            return self._ai_client_instance

        if ai_client_instance := get_ai_client():
            self._ai_client_instance = ai_client_instance
            return ai_client_instance

        raise ValueError("AI client not found")

    def _fetch_messages(
        self,
    ) -> list[ChatInteraction]:
        if not self.has_checked_database:
            with rx.session() as session:
                self.has_checked_database = True
                query = select(ChatInteraction)
                if self.filter:
                    query = query.where(
                        or_(
                            ChatInteraction.prompt.ilike(f"%{self.filter}%"),
                            ChatInteraction.answer.ilike(f"%{self.filter}%"),
                        ),
                    )

                return (
                    session.exec(
                        query.distinct(ChatInteraction.prompt)
                        .order_by(ChatInteraction.timestamp.desc())
                        .limit(MAX_QUESTIONS),
                    )
                    .scalars()
                    .all()
                )

        return []

    def load_messages_from_database(
        self,
    ) -> None:
        self.chat_interactions = self._fetch_messages()

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

    async def _check_saved_chat_interactions(
        self,
        username: str,
        prompt: str,
    ) -> None:
        with rx.session() as session:
            if (
                session.exec(
                    select(ChatInteraction)
                    .where(
                        ChatInteraction.chat_participant_user_name == username,
                    )
                    .where(
                        ChatInteraction.prompt == prompt,
                    ),
                ).first()
                or len(
                    session.exec(
                        select(ChatInteraction)
                        .where(
                            ChatInteraction.chat_participant_user_name == username,
                        )
                        .where(
                            ChatInteraction.timestamp
                            > datetime.datetime.now()
                            - datetime.timedelta(
                                days=1,
                            ),
                        ),
                    ).all(),
                )
                > MAX_QUESTIONS
            ):
                raise ValueError(
                    "You have already asked this question or have asked too many questions in the past 24 hours.",
                )

    @rx.event(background=True)
    async def submit_prompt(
        self,
    ):
        async def _fetch_chat_completion_session(
            prompt: str,
        ):
            def _create_messages_for_chat_completion():
                messages = [
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": "You are a helpful assistant. Respond in markdown.",
                            },
                        ],
                    },
                ]
                for chat_interaction in self.chat_interactions:
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": chat_interaction.prompt,
                                },
                            ],
                        },
                    )
                    messages.append(
                        {
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "text",
                                    "text": chat_interaction.answer,
                                },
                            ],
                        },
                    )

                messages.append(
                    {
                        "role": "user",
                        "content": prompt,
                    },
                )
                return messages

            messages = _create_messages_for_chat_completion()
            client_instance: Together = self._get_client_instance()
            stream = client_instance.chat.completions.create(
                model=AI_MODEL,
                messages=messages,
                max_tokens=512,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["<|eot_id|>", "<|eom_id|>"],
                truncate=130560,
                stream=True,
            )
            if stream is None:
                raise Exception("Session is None")

            return stream

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
                ),
            )
            self.prompt = ""

        # Get the question from the form
        if self.prompt == "":
            return

        prompt = self.prompt
        if self.username == "":
            raise ValueError("Username is required")

        await self._check_saved_chat_interactions(
            prompt=prompt,
            username=self.username,
        )
        async with self:
            set_ui_loading_state()

            yield

            with using_prompt_template(
                template=prompt,
            ):
                stream = await _fetch_chat_completion_session(prompt)
                clear_ui_loading_state()
                add_new_chat_interaction()
                yield

                try:
                    for item in stream:
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
        self._save_resulting_chat_interaction(
            chat_interaction=self.chat_interactions[-1],
        )
