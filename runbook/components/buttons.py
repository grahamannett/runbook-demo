from typing import Any, Callable

import reflex as rx

from runbook.components.loading_icon import loading_icon
from runbook.page_chat.chat_state import ChatState
from runbook.templates.style import BaseStyle

ButtonStyle = BaseStyle(**{"radius": "large", "cursor": "pointer", "padding": "18px 16px"})


def button_with_icon(
    text: str,
    icon: str | None = None,
    on_click: Callable | None = None,  #  lambda: None,
    is_loading: bool = False,
    **kwargs,
):
    """Creates a button with an icon.
    - text: The text of the button.
    - icon: The icon tag name.
    - **kwargs: Additional keyword arguments for rx.button.
    """

    def _show_icon():
        if icon is None:
            return rx.box()

        return rx.icon(tag=icon, size=18)

    return rx.button(
        rx.cond(
            is_loading,
            loading_icon(
                height="1em",
            ),
            rx.hstack(
                _show_icon(),
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
        on_click=on_click,
        **ButtonStyle,
        **kwargs,
    )


def llm_provider_dialog():
    return rx.dialog.root(
        rx.dialog.trigger(rx.icon(tag="cherry")),
        rx.dialog.content(
            rx.dialog.title("Edit Provider"),
            rx.dialog.description(
                "Change provider and API key.",
                size="2",
                margin_bottom="16px",
            ),
            rx.flex(
                rx.text(
                    "Provider",
                    as_="div",
                    size="2",
                    margin_bottom="4px",
                    weight="bold",
                ),
                rx.input(
                    default_value=ChatState.ai_provider,
                    placeholder="Pick provider",
                    on_blur=ChatState.set_ai_provider,
                ),
                rx.text(
                    "Endpoint URL",
                    as_="div",
                    size="2",
                    margin_bottom="4px",
                    weight="bold",
                ),
                rx.input(
                    default_value=ChatState.ai_provider_url,
                    placeholder="Enter the endpoint URL",
                    on_blur=ChatState.set_ai_provider_url,
                ),
                rx.text(
                    "API Key",
                    as_="div",
                    size="2",
                    margin_bottom="4px",
                    weight="bold",
                ),
                rx.input(
                    default_value=ChatState.ai_provider_api_key,
                    placeholder="Enter the API key",
                    on_blur=ChatState.set_ai_provider_api_key,
                ),
                direction="column",
                spacing="3",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        color_scheme="gray",
                        variant="soft",
                    ),
                ),
                rx.dialog.close(
                    rx.button("Save"),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
    )
