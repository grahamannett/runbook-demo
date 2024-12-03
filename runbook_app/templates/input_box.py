from typing import Callable

import reflex as rx

from runbook_app.components.badges import badge_with_icon
from runbook_app.components.buttons import button_with_icon
from runbook_app.page_chat.chat_state import ChatState
from runbook_app.templates.pop_up import LibraryDocument, LibraryPrompt


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


def list_of_document_components(border: str):
    # Document list
    return rx.vstack(
        rx.foreach(
            ChatState.documents,
            lambda doc: rx.hstack(
                rx.vstack(
                    rx.heading(doc["title"], size="sm"),
                    rx.text(doc["url"], font_size="xs", color="gray"),
                    align_items="start",
                ),
                rx.spacer(),
                badge_with_icon("View", "eye"),
                width="100%",
                padding="2",
                border_bottom=border,
            ),
        ),
        width="100%",
        max_height="400px",
        overflow_y="auto",
    )


def use_document_library():
    return rx.dialog.root(
        rx.dialog.trigger(
            button_with_icon(
                "Documents",
                "panel-top",
                on_click=LibraryDocument.toggle_document_library,
            )
        ),
        rx.dialog.content(
            rx.dialog.title(
                rx.text("Document Library"),
                # rx.dialog.description("View loaded documents and add new ones by URL."),
            ),
            rx.vstack(
                # URL Input section
                rx.form(
                    rx.hstack(
                        rx.input(
                            placeholder="Enter document URL...",
                            # value=LibraryDocument.url_input,
                            # on_change=LibraryDocument.set_url_input,
                            width="100%",
                        ),
                        rx.button(
                            "Add",
                            type="submit",
                            # is_loading=LibraryDocument.processing,
                        ),
                    ),
                    # on_submit=ChatState.process_url,
                ),
                # rx.cond(
                #     LibraryDocument.error,
                #     rx.text(
                #         LibraryDocument.error,
                #         color="red",
                #         font_size="sm",
                #     ),
                # ),
                width="100%",
                spacing="4",
            ),
            rx.dialog.close(
                rx.icon(tag="x"),
            ),
        ),
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
                use_document_library(),
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
