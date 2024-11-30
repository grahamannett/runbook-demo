from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import reflex as rx

from runbook_app.page_chat.chat_state import AuthState

from .loading_icon import loading_icon


@dataclass
class Style:
    default: dict[str, str | rx.Component] = field(
        default_factory=lambda: {
            "radius": "large",
            "cursor": "pointer",
            "variant": "classic",
            "padding": "18px 16px",
        },
    )


BUTTON_STYLE: Style = Style()


def logout_button():
    """Creates a logout button."""
    logout_style = {**BUTTON_STYLE.default, "background": "salmon"}
    return rx.button(
        "Logout",
        on_click=AuthState.logout,
        **logout_style,
    )


def button_with_icon(
    text: str,
    icon: str,
    on_click: Callable = lambda: None,
    is_loading: bool = False,
    **kwargs,
):
    """Creates a button with an icon.
    - text: The text of the button.
    - icon: The icon tag name.
    - **kwargs: Additional keyword arguments for rx.button.
    """
    return rx.button(
        rx.cond(
            is_loading,
            loading_icon(
                height="1em",
            ),
            rx.hstack(
                rx.icon(
                    tag=icon,
                    size=14,
                ),
                rx.text(
                    text,
                    size="2",
                    align="center",
                    weight="medium",
                    font_family="Inter",
                ),
                gap="8px",
                width="100%",
                display="flex",
                align="center",
                justify="center",
            ),
        ),
        **BUTTON_STYLE.default,
        **kwargs,
        on_click=on_click,
    )
