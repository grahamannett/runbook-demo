import reflex as rx

from runbook_app.page_chat.chat_page import chat_page
from runbook_app.page_chat.chat_state import ChatState, require_login
from runbook_app.templates.pop_up import LibraryDocument

app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap",
    ],
)


@require_login
def index():
    return chat_page()


app.add_page(index, route="/", on_load=[ChatState.on_load_index])
