from datetime import datetime
from typing import Any

import reflex as rx

from runbook.components.dividers import chat_date_divider
from runbook.components.typography import msg_header
from runbook.db_models import ChatInteraction
from runbook.page_chat.style import LLMResponseStyle, UserMessageStyle
from runbook.templates.action_bar import action_bar
from runbook.templates.pop_up import dialog_library
from runbook.templates.style import BaseStyle

AvatarStyle = BaseStyle(**{"fallback": "R", "size": "2", "border_radius": "100%"})
MessageTextStyle = BaseStyle(
    **{
        "width": "100%",
        "overflow_wrap": "break_word",
        "color": rx.color(color="slate", shade=11),
    }
)


def message_part_component(
    *message_children,
    avatar: rx.Component,
    header: rx.Component,
    message: rx.Component,
    style_props: dict[str, Any] | BaseStyle = {},
    timestamp: datetime | None = None,
):
    return rx.box(
        rx.hstack(
            rx.box(avatar),
            rx.vstack(
                header,
                message,
                *message_children,
            ),
        ),
        **style_props,
    )


def bot_response_buttons():
    return rx.box(
        "CSS color",
        background_color="red",
        border_radius="2px",
        width="100%",
        margin_y="10px",
    )


def message_wrapper(chat_interaction: ChatInteraction):
    user_ava = rx.avatar(src=chat_interaction.chat_participant_user_name, **AvatarStyle)
    rb_ava = rx.avatar(src=chat_interaction.chat_participant_assistant_name, **AvatarStyle)

    user_header = msg_header(chat_interaction.chat_participant_user_name, chat_interaction.timestamp)
    rb_header = msg_header(chat_interaction.chat_participant_assistant_name, chat_interaction.timestamp)

    user_message = rx.markdown(chat_interaction.prompt, **MessageTextStyle)
    rb_message = rx.markdown(chat_interaction.answer, **MessageTextStyle)

    return rx.box(
        # this component is related to the user input
        message_part_component(
            avatar=user_ava,
            header=user_header,
            message=user_message,
            style_props=UserMessageStyle,
        ),
        # this component is related to the bot response
        message_part_component(
            # bot_response_buttons(),
            avatar=rb_ava,
            header=rb_header,
            message=rb_message,
            style_props=LLMResponseStyle,
        ),
    )


def chat_body(
    chat_interactions: list[ChatInteraction],
    divider_title_text: str,
):
    return rx.vstack(
        chat_date_divider(divider_title_text=divider_title_text),
        rx.scroll_area(
            rx.vstack(
                rx.foreach(chat_interactions, message_wrapper),
                gap="2em",
            ),
            scrollbars="vertical",
            type="scroll",
            # style={"height": "50vh"},
        ),
        dialog_library(),
        width="100%",
        overflow="scroll",
        scrollbar_width="none",
        gap="40px",
    )
