import reflex as rx

from runbook_app.templates.style import BaseStyle

SharedStyle = BaseStyle(
    **{
        "gap": "12px",
        "display": "flex",
        "border_radius": "16px",
    }
)


# Question-specific style
UserMessageStyle = BaseStyle(
    **SharedStyle,  # Now we can unpack directly from the style instance
    justify="flex-start",
    align_self="flex-start",
)


# Answer-specific style
LLMResponseStyle = BaseStyle(
    **SharedStyle,  # Now we can unpack directly from the style instance
    justify="flex-start",
    align_self="flex-end",
    padding="24px",
    background=rx.color(color="indigo", shade=2),
    box_shadow="0px 2px 4px rgba(25, 33, 61, 0.08)",
    border=rx.color_mode_cond(
        light=f"2px solid {rx.color('indigo', 3)}",
        dark="",
    ),
)
