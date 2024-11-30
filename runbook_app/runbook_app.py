import functools
import os

import reflex as rx
from reflex.utils.exec import is_prod_mode

from .page_chat.chat_page import chat_page
from .page_chat.chat_state import INPUT_BOX_ID, AuthState, ChatState

app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap",
    ],
)


def is_dev_mode():
    if os.environ.get("DEV_MODE"):
        return False
    if not is_prod_mode():
        return True
    return False


def signin():
    return rx.box(
        rx.heading("Enter App Password"),
        rx.form(
            rx.input(
                placeholder="app password",
            ),
            on_submit=AuthState.handle_submit,
        ),
    )


def require_login(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    if is_dev_mode():
        return page

    @functools.wraps(page)
    def protected_page() -> rx.Component:
        return rx.box(
            rx.cond(
                AuthState.is_hydrated,
                rx.cond(AuthState.valid_session, page(), signin()),
                rx.spinner(),
            ),
        )

    return protected_page


@require_login
def index():
    return chat_page(
        input_box_id=INPUT_BOX_ID,
    )


app.add_page(index, route="/", on_load=ChatState.load_messages_from_database)
