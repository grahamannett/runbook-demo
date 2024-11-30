from typing import Callable

import reflex as rx

from runbook_app.components.buttons import button_with_icon

from .pop_up import DocumentLibrary, LibraryPrompt


def use_library_button(library_prompt: LibraryPrompt, input_box_id: str):
    return rx.button(
        rx.icon(tag="book", size=18),
        "Library",
        radius="large",
        cursor="pointer",
        padding="18px 16px",
        bg="transparent",
        border=rx.color_mode_cond(
            light="1px solid indigo",
            dark="1px solid slate",
        ),
        color=rx.color(
            color="slate",
            shade=11,
        ),
        on_click=library_prompt.toggle_prompt_library,
        id=input_box_id,
    )


def use_document_button():
    def on_click():
        return rx.toast("Document button clicked!")

    return rx.button(
        rx.icon(tag="panel-top", size=18),
        "Documents",
        radius="large",
        cursor="pointer",
        padding="18px 16px",
        bg="transparent",
        border=rx.color_mode_cond(
            light="1px solid indigo",
            dark="1px solid slate",
        ),
        color=rx.color(
            color="slate",
            shade=11,
        ),
        on_click=on_click,
    )


def input_box(
    input_box_id: str,
    input_box_text_value: str,
    input_prompt_is_loading: bool,
    input_prompt_on_change: Callable,
    send_button_on_click: Callable,
    library_prompt: LibraryPrompt,
    **kwargs,
):
    return rx.vstack(
        rx.input(
            rx.input.slot(
                rx.tooltip(
                    rx.icon(
                        "info",
                        size=18,
                    ),
                    content="Enter a question to get a response.",
                ),
            ),
            value=input_box_text_value,
            placeholder="Generate a runbook for which task",
            on_change=input_prompt_on_change,
            height="75px",
            width="100%",
            background_color=rx.color(
                color="indigo",
                shade=2,
            ),
            variant="soft",
            outline="none",
            line_height="150%",
            color=rx.color(
                color="slate",
                shade=11,
            ),
            **kwargs,
        ),
        rx.divider(),
        rx.hstack(
            rx.hstack(
                use_library_button(library_prompt=library_prompt, input_box_id=input_box_id),
                rx.spacer(),
                use_document_button(),
                display="flex",
                align="center",
            ),
            button_with_icon(
                text="Send Message",
                icon="send",
                is_loading=input_prompt_is_loading,
                on_click=send_button_on_click,
            ),
            width="100%",
            display="flex",
            justify="between",
        ),
        width="100%",
        display="flex",
        align="start",
        padding="24px",
        gap="16px 24px",
        border_radius="16px",
        border=rx.color_mode_cond(
            f"2px solid {rx.color('indigo', 3)}",
            f"1px solid {rx.color('slate', 7, True)}",
        ),
        background_color=rx.color(
            color="indigo",
            shade=2,
        ),
        box_shadow=rx.color_mode_cond(
            light="0px 1px 3px rgba(25, 33, 61, 0.1)",
            dark="none",
        ),
    )
