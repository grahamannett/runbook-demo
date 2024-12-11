from typing import Callable

import reflex as rx

from runbook.components.buttons import ButtonStyle, button_with_icon, llm_provider_dialog
from runbook.page_chat.chat_state import ChatState
from runbook.templates.style import BaseStyle

NavBarStyle = BaseStyle(
    **{
        "width": "100%",
        "display": "flex",
        "justify": "between",
        "padding": "16px 24px",
        "border_bottom": rx.color_mode_cond(
            light=f"2px solid {rx.color('indigo', 3)}",
            dark=f"1px solid {rx.color('slate', 7, True)}",
        ),
    }
)

NavBarComponentStyle = BaseStyle(**{"width": "400px", "display": "flex", "align": "center", "spacing": "6"})


def nav_bar(chat_state: ChatState):
    return rx.hstack(
        rx.hstack(
            button_with_icon(text="Logout", on_click=chat_state.handle_logout, background="salmon"),
            rx.color_mode.button(),
            llm_provider_dialog(),
            **NavBarComponentStyle,
        ),
        button_with_icon(
            text="New Runbook",
            icon="plus",
            on_click=chat_state.create_new_runbook,
        ),
        **NavBarStyle,
    )
