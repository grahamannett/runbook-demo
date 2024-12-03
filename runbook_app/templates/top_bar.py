from typing import Callable

import reflex as rx

from runbook_app.components.buttons import button_with_icon, llm_provider_dialog, logout_button
from runbook_app.templates.style import BaseStyle

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

NavBarComponentStyle = BaseStyle(
    **{
        "width": "400px",
        "display": "flex",
        "align": "center",
        "spacing": "6",
    }
)


def nav_bar(
    on_create_new_chat: Callable,
):
    return rx.hstack(
        rx.hstack(
            # toggle theme
            logout_button(),
            rx.color_mode.button(),
            llm_provider_dialog(),
            **NavBarComponentStyle,
        ),
        button_with_icon(
            text="New Runbook",
            icon="plus",
            on_click=on_create_new_chat,
        ),
        **NavBarStyle,
    )
