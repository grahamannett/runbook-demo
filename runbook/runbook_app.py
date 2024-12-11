import reflex as rx

from runbook.page_chat.chat_page import chat_page
from runbook.page_chat.chat_state import ChatState
from runbook.utils import make_require_login

app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap",
    ],
)


require_login = make_require_login(chat_state=ChatState)


@require_login
def index():
    return chat_page()


app.add_page(index, route="/", on_load=[ChatState.on_load_index])
