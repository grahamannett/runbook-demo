import reflex as rx

from runbook.components.badges import badge_with_icon
from runbook.components.buttons import button_with_icon
from runbook.components.document_library import document_source_card
from runbook.page_chat.chat_state import ChatState
from runbook.templates.pop_up import LibraryDocument, LibraryPrompt
from rxconstants import INPUT_BOX_ID


def use_library_button():
    return rx.button(
        rx.icon(tag="book", size=18),
        "Library",
        radius="large",
        cursor="pointer",
        padding="18px 16px",
        bg="transparent",
        border=rx.color_mode_cond(light="1px solid indigo", dark="1px solid slate"),
        color=rx.color(color="slate", shade=11),
        on_click=LibraryPrompt.toggle_library,
    )


def list_of_document_components(border: str):
    # Document list
    return rx.vstack(
        rx.foreach(
            ChatState.document_sources,
            lambda doc: rx.hstack(
                rx.vstack(
                    rx.heading(doc["title"], size="sm"),
                    rx.text(doc["url"], font_size="xs", color="gray"),
                    align_items="start",
                ),
                rx.spacer(),
                # badge_with_icon("View", "eye"),
                width="100%",
                padding="2",
                border_bottom=border,
            ),
        ),
        width="100%",
        max_height="400px",
        overflow_y="auto",
    )


def add_document_component():
    return rx.vstack(
        # URL Input section
        rx.form(
            rx.hstack(
                rx.input(placeholder="Enter document URL...", name="url", width="100%"),
                rx.button("Add", type="submit", loading=ChatState.processing_document),
            ),
            on_submit=ChatState.add_document,
        ),
        width="100%",
        spacing="4",
    )


def use_document_library():
    # default_open = ChatState.len_documents <= 0
    default_open = True
    return rx.dialog.root(
        rx.dialog.trigger(
            button_with_icon(
                f"Documents[{ChatState.len_documents}]",
                "panel-top",
                on_click=LibraryDocument.toggle_library,
            )
        ),
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.text("Document Library"),
                    rx.spacer(),
                    rx.dialog.close(rx.icon(tag="x", on_click=LibraryDocument.toggle_library)),
                ),
                rx.dialog.description("View loaded documents and add new ones by URL."),
            ),
            rx.flex(
                rx.vstack(rx.foreach(ChatState.document_sources, document_source_card)),
                rx.divider(size="4"),
                add_document_component(),
                direction="column",
                spacing="4",
            ),
        ),
        default_open=default_open,
    )


def input_box(chat_state: ChatState, **kwargs):
    return rx.vstack(
        rx.input(
            rx.input.slot(
                rx.tooltip(rx.icon("info", size=18), content="Enter a question to get a response."),
            ),
            value=chat_state.prompt,
            placeholder="Generate a runbook for which task",
            on_change=chat_state.set_prompt,
            height="75px",
            width="100%",
            background_color=rx.color(color="indigo", shade=2),
            variant="soft",
            outline="none",
            line_height="150%",
            color=rx.color(color="slate", shade=11),
            **kwargs,
        ),
        rx.divider(),
        rx.hstack(
            rx.hstack(
                use_library_button(),
                rx.spacer(),
                use_document_library(),
                display="flex",
                align="center",
            ),
            button_with_icon(
                text=ChatState.send_message_text,
                icon="send",
                is_loading=chat_state.ai_loading,
                on_click=chat_state.submit_prompt,
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
        background_color=rx.color(color="indigo", shade=2),
        box_shadow=rx.color_mode_cond(light="0px 1px 3px rgba(25, 33, 61, 0.1)", dark="none"),
        id=INPUT_BOX_ID,
    )
