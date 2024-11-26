import functools

import reflex as rx

from runbook_app.templates.input_box import input_box
from runbook_app.templates.pop_up import LibraryPrompt
from runbook_app.templates.top_bar import nav_bar

from .chat_body import chat_body
from .chat_state import ChatState
from .style import Style

STYLE: Style = Style()


def _chat_box(
    chat_state: ChatState,
    input_box_id: str,
) -> rx.Component:
    return rx.box(
        rx.vstack(
            nav_bar(
                on_create_new_chat=chat_state.create_new_chat,
            ),
            chat_body(
                chat_interactions=chat_state.chat_interactions,
                has_token=chat_state.has_token,
                divider_title_text=chat_state.timestamp_formatted,
            ),
            input_box(
                input_box_text_value=chat_state.prompt,
                input_prompt_is_loading=chat_state.ai_loading,
                input_prompt_on_change=chat_state.set_prompt,
                send_button_on_click=chat_state.submit_prompt,
                library_prompt=LibraryPrompt,
                input_box_id=input_box_id,
            ),
            **STYLE.body,
        ),
        **STYLE.parent,
    )


def require_login(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    @functools.wraps(page)
    def protected_page() -> rx.Component:
        return rx.box(
            rx.cond(
                AuthState.is_hydrated,
                rx.cond(AuthState.valid_session, page(), signin_page()),
                rx.spinner(),
            ),
        )

    return protected_page

def chat_page(
    chat_state: ChatState,
    input_box_id: str,
):
    return _chat_box(
        chat_state=chat_state,
        input_box_id=input_box_id,
    )
