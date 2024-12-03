from datetime import datetime
from typing import Any

import reflex as rx

from runbook_app.components.dividers import chat_date_divider
from runbook_app.components.typography import msg_header
from runbook_app.db_models import ChatInteraction
from runbook_app.page_chat.style import ANSWER_STYLE, QUESTION_STYLE
from runbook_app.templates.pop_up import dialog_library

answer_style_kwargs: dict[str, Any] = ANSWER_STYLE.default
question_style_kwargs: dict[str, Any] = QUESTION_STYLE.default


def message_part_component(
    *message_children,
    user_name: str,
    message: str,
    style_kwargs: dict[str, Any],
    timestamp: datetime | None = None,
    avatar_url: str | None = None,
    avatar_fallback: str = "R",
):
    return rx.hstack(
        rx.vstack(
            rx.avatar(
                src=avatar_url,
                fallback=avatar_fallback,
                size="2",
                border_radius="100%",
            ),
        ),
        rx.vstack(
            msg_header(
                header_title=user_name,
                date=timestamp,
            ),
            rx.markdown(
                message,
                color=rx.color(
                    color="slate",
                    shade=11,
                ),
            ),
            *message_children,
            overflow_wrap="break_word",
            width="100%",
        ),
        **style_kwargs,
    )


def bot_response_buttons():
    return rx.box(
        "CSS color",
        background_color="red",
        border_radius="2px",
        width="100%",
        margin_y="10px",
    )


def message_wrapper(
    chat_interaction: ChatInteraction,
    has_token: bool,
):
    return rx.fragment(
        # this component is related to the user input
        message_part_component(
            user_name=chat_interaction.chat_participant_user_name,
            timestamp=chat_interaction.timestamp,
            message=chat_interaction.prompt,
            style_kwargs=question_style_kwargs,
            avatar_url=chat_interaction.chat_participant_user_avatar_url,
        ),
        # this component is related to the bot response
        message_part_component(
            # bot_response_buttons(),
            user_name=chat_interaction.chat_participant_assistant_name,
            timestamp=chat_interaction.timestamp,
            message=chat_interaction.answer,
            style_kwargs=answer_style_kwargs,
            avatar_url=chat_interaction.chat_participant_assistant_avatar_url,
        ),
    )


def chat_body(
    chat_interactions: list[ChatInteraction],
    divider_title_text: str,
    has_token: bool,
):
    return rx.vstack(
        chat_date_divider(
            divider_title_text=divider_title_text,
        ),
        rx.scroll_area(
            rx.vstack(
                rx.foreach(
                    chat_interactions,
                    lambda chat_interaction: message_wrapper(
                        chat_interaction=chat_interaction,
                        has_token=has_token,
                    ),
                ),
                gap="2em",
            ),
            scrollbars="vertical",
            type="scroll",
        ),
        dialog_library(),
        width="100%",
        overflow="scroll",
        scrollbar_width="none",
        gap="40px",
    )
