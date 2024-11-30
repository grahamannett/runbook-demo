from dataclasses import dataclass, field
from typing import Any

import reflex as rx

from runbook_app.templates.style import Style as TemplateStyle


@dataclass
class Style(TemplateStyle):
    component_wrapper: dict[str, str | Any] = field(
        default_factory=lambda: {
            "top": "0",
            "right": "0",
            "width": "100%",
            "z_index": "10",
            "height": "100%",
            "padding": "32px",
            "max_width": "450px",
            "background": rx.color(
                color="indigo",
                shade=1,
            ),
            "border_left": rx.color_mode_cond(
                f"1px solid {rx.color('indigo', 3)}",
                f"1px solid {rx.color('slate', 7, True)}",
            ),
        },
    )
