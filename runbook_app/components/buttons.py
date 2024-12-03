from typing import Any, Callable

import reflex as rx

from runbook_app.components.loading_icon import loading_icon
from runbook_app.page_chat.chat_state import AuthState, ChatState
from runbook_app.templates.style import BaseStyle

ButtonStyle = BaseStyle(
    **{
        "radius": "large",
        "cursor": "pointer",
        "padding": "18px 16px",
    },
)


def logout_button():
    """Creates a logout button."""
    return rx.button(
        "Logout",
        on_click=AuthState.logout,
        **{
            **ButtonStyle,
            "background": "salmon",
        },
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
                # rx.dialog.close(
                #     rx.button("Print info", on_click=ChatState.print_ai_info),
                # ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
    )
