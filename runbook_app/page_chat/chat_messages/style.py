from dataclasses import dataclass, field
from typing import Any

import reflex as rx


@dataclass
class Style:
    default: dict[str, str | Any] = field(
        default_factory=lambda: {
            "gap": "12px",
            "display": "flex",
            "border_radius": "16px",
        },
    )


QUESTION_STYLE: Style = Style()
QUESTION_STYLE.default.update(
    {
        "justify": "flex-start",
        "align_self": "flex-start",
    },
)


ANSWER_STYLE: Style = Style()
ANSWER_STYLE.default.update(
    {
        "justify": "flex-start",
        "align_self": "flex-end",
        "padding": "24px",
        "background": rx.color(
            color="indigo",
            shade=2,
        ),
        "box_shadow": "0px 2px 4px rgba(25, 33, 61, 0.08)",
        "border": rx.color_mode_cond(
            light=f"2px solid {rx.color('indigo', 3)}",
            dark="",
        ),
    },
)
