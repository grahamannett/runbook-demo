from typing import Callable

import reflex as rx

from runbook.components.badges import badge_with_icon
from runbook.components.buttons import button_with_icon
from runbook.rag_tools import load_all_documents
from runbook.templates.search_box import search_bar_with_sidebar_shortcut
from runbook.templates.select import select_menu

__prompts__ = []


class PromptLibrary(rx.State):
    def create_new_prompt_entry(self) -> None:
        pass


# WARN: cannot make these both subclasses of parent rx.State as it doesn't work with reflex
class LibraryPrompt(rx.State):
    is_open: bool = False

    def toggle_library(self) -> None:
        self.is_open = not self.is_open


class LibraryDocument(rx.State):
    is_open: bool = False

    def toggle_library(self) -> None:
        self.is_open = not self.is_open


def popup_menu():
    border = rx.color_mode_cond(
        f"1px solid {rx.color('indigo', 3)}",
        f"1px solid {rx.color('slate', 7, True)}",
    )

    background = rx.color_mode_cond(
        rx.color("indigo", 1),
        rx.color("indigo", 3),
    )

    box_shadow = rx.color_mode_cond("0px 1px 3px rgba(25, 33, 61, 0.1)", "none")

    return rx.vstack(
        rx.hstack(
            search_bar_with_sidebar_shortcut(width="100%"),
            select_menu("list-filter", "Sort by"),
            width="100%",
        ),
        rx.hstack(
            rx.hstack(
                button_with_icon(
                    "Create",
                    "plus",
                    disabled=True,
                    on_click=PromptLibrary.create_new_prompt_entry,
                ),
                rx.spacer(),
                rx.box(
                    rx.icon(tag="folder", size=15, color=rx.color("slate", 11)),
                    border=border,
                    padding="10px",
                    border_radius="8px",
                ),
                width="100%",
                align="center",
                justify="end",
            ),
            width="100%",
            align="center",
            justify="between",
        ),
        width="100%",
        spacing="4",
        padding="5px 0px 16px 0px",
    )


def prompt_item(
    title: str,
    description: str,
):
    return rx.hstack(
        rx.vstack(
            rx.text(title, weight="bold", color=rx.color("slate", 12)),
            rx.text(
                description,
                width="100%",
                overflow="hidden",
                font_family="Inter",
                white_space="nowrap",
                text_overflow="ellipsis",
                color=rx.color("slate", 11),
            ),
            flex="3",
            justify="center",
            align="start",
            spacing="1",
            overflow_x="hidden",
        ),
        rx.hstack(
            *[badge_with_icon(name) for name in ["move-up-right", "ellipsis-vertical"]],
            flex="1",
            align="center",
            justify="end",
        ),
        width="100%",
        align="center",
        justify="between",
        gap="16px",
        border_bottom=rx.color_mode_cond(
            f"2px solid {rx.color('indigo', 3)}",
            f"1px solid {rx.color('slate', 7, True)}",
        ),
        padding_bottom="16px",
    )


def list_prompt_component(prompt_items: list[dict]):
    return rx.vstack(
        *[prompt_item(title, description) for title, description in prompt_items],
        width="100%",
        height="30em",
        overflow="scroll",
        spacing="5",
        padding="16px 0px",
    )


def dialog_library_base(
    *args,
    on_create_new_chat: Callable,
):
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.text("Runbook Library"),
                    rx.dialog.close(
                        rx.icon(tag="x", size=20),
                        on_click=LibraryPrompt.toggle_library,
                    ),
                    width="100%",
                    align="center",
                    justify="between",
                )
            ),
            rx.dialog.description(
                popup_menu(),
                rx.divider(),
                *args,
                width="100%",
                gap="12px",
            ),
            rx.box(
                position="absolute",
                bottom="0",
                left="0",
                width="100%",
                height="20%",
                background=f"linear-gradient(360deg,{rx.color('indigo', 2)}, transparent);",
                gap="40px",
            ),
            background_color=rx.color_mode_cond(
                "",
                rx.color(
                    "indigo",
                    2,
                ),
            ),
            height="40em",
            overflow="hidden",
            on_interact_outside=LibraryPrompt.toggle_library,
        ),
        open=LibraryPrompt.is_open,
    )


def dialog_library():
    return dialog_library_base(
        list_prompt_component(prompt_items=__prompts__),
        on_create_new_chat=PromptLibrary.create_new_prompt_entry,
    )
