from dataclasses import dataclass, field
from typing import Any, Callable

import reflex as rx

from runbook_app.components.buttons import button_with_icon, logout_button


@dataclass
class Style:
    """
    Style for the top bar.

    Previously had the following icons listed: "settings", "trash", "archive", "panel-right"

    """

    default: dict[str, str | rx.Component | rx.Var] = field(
        default_factory=lambda: {
            "width": "100%",
            "display": "flex",
            "justify": "between",
            "padding": "16px 24px",
            "border_bottom": rx.color_mode_cond(
                light=f"2px solid {rx.color('indigo', 3)}",
                dark=f"1px solid {rx.color('slate', 7, True)}",
            ),
        },
    )

    component: dict[str, str] = field(
        default_factory=lambda: {
            "width": "400px",
            "display": "flex",
            "align": "center",
            "spacing": "6",
        },
    )


NAV_BAR_STYLE: Style = Style()
nav_bar_style_component_kwargs: dict[str, Any] = NAV_BAR_STYLE.component
nav_bar_style_default_kwargs: dict[str, Any] = NAV_BAR_STYLE.default


def nav_bar(
    on_create_new_chat: Callable,
):
    return rx.hstack(
        rx.hstack(
            # toggle theme
            logout_button(),
            rx.color_mode.button(),
            **nav_bar_style_component_kwargs,
        ),
        button_with_icon(
            text="New Chat",
            icon="plus",
            on_click=on_create_new_chat,
        ),
        **nav_bar_style_default_kwargs,
    )
