import reflex as rx

from runbook_app.page_chat.chat_body import chat_body
from runbook_app.page_chat.chat_state import ChatState
from runbook_app.templates.input_box import input_box
from runbook_app.templates.style import BaseStyle
from runbook_app.templates.top_bar import nav_bar

body_style = BaseStyle(
    width="100%",
    max_width="50em",
    height="100%",
    display="flex",
    overflow="hidden",
    padding_bottom="30px",
    margin_inline="auto",
)

parent_style = BaseStyle(
    gap="40px",
    z_index="10",
    width="100%",
    height="100%",
)


def chat_page(chat_state: type[ChatState] = ChatState):
    return rx.box(
        rx.cond(
            chat_state.is_hydrated,
            rx.box(
                rx.vstack(
                    nav_bar(chat_state=chat_state),
                    rx.spacer(),
                    chat_body(
                        chat_interactions=chat_state.chat_interactions,
                        divider_title_text=chat_state.timestamp_formatted,
                    ),
                    input_box(chat_state=chat_state),
                    **body_style,
                ),
                **parent_style,
            ),
        ),
    )
