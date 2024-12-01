import reflex as rx

from runbook_app.templates.style import BaseStyle

BadgeStyle = BaseStyle(
    **{
        "width": "35px",
        "height": "35px",
        "border_radius": "4px",
        "box_shadow": "0px 1px 3px rgba(25, 33, 61, 0.1)",
        "background": rx.color_mode_cond(
            rx.color(
                color="indigo",
                shade=1,
            ),
            "#49557A",
        ),
    }
)


def badge_with_icon(
    icon: str,
):
    return rx.badge(
        rx.icon(
            tag=icon,
            size=18,
            stroke_width="2px",
            color=f"{rx.color('slate', 11, True)}",
        ),
        **BadgeStyle,
        display="flex",
        align_items="center",
        justify_content="center",
    )


def sidebar_shortcut(
    char: str,
    **kwargs,
):
    """Creates a badge with an icon.
    - char: The character of the shortcut.
    - **kwargs: Additional keyword arguments for rx.button.
    """
    return rx.badge(
        rx.hstack(
            rx.icon(
                tag="command",
                size=14,
                color=f"{rx.color('slate', 11, True)}",
            ),
            rx.text(
                char,
                weight="regular",
                size="1",
                align="center",
                font_family="Inter",
                color=f"{rx.color('slate', 11, True)}",
            ),
            width="100%",
            display="flex",
            align="center",
            justify="center",
            gap="4px",
        ),
        **BadgeStyle,
        **kwargs,
    )
