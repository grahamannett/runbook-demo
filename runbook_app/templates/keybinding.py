import reflex as rx

from runbook_app.components.badges import sidebar_shortcut
from runbook_app.components.typography import text_with_icon
from runbook_app.templates.style import BaseStyle

KeybindingStyle = BaseStyle(
    **{
        "width": "100%",
        "display": "flex",
        "align": "center",
        "justify": "between",
        "padding": "8px 5px 8px 10px",
        "border_radius": "8px",
    }
)

SHORTCUT = {
    "width": "100%",
    "display": "flex",
    "align": "center",
    "justify": "between",
    "padding": "8px 5px 8px 10px",
    "border_radius": "8px",
}


def keybinding(
    icon: str,
    name: str,
    key_binding: str,
    **kwargs,
):
    """Creates a text to key-binding shortcut.
    - icon: The icon tag name.
    - name: The name of the shortcut.
    - key_binding: The character representation of the shortcut.
    - **kwargs: Additional keyword arguments for rx.button.
    """
    kwargs = {**KeybindingStyle, **kwargs}
    return rx.hstack(
        text_with_icon(icon, name),
        sidebar_shortcut(key_binding),
        **kwargs,
    )
