import datetime

import reflex as rx


def text_with_icon(
    icon: str,
    text: str,
    **kwargs,
):
    """Creates a text with an icon.
    - icon: The icon tag name.
    - text: The title name.
    - kwargs: Additonal props for the component.
    """
    return rx.hstack(
        rx.icon(
            tag=icon,
            size=16,
        ),
        rx.text(
            text,
            size="2",
            weight="regular",
            font_family="Inter",
            overflow="hidden",
            white_space="nowrap",
        ),
        **kwargs,
        width="220px",
        display="flex",
        align="center",
        justify="start",
        color=rx.color(
            color="slate",
            shade=11,
        ),
    )


def sidebar_text(
    name: str,
    **kwargs,
):
    """Creates a text with ellipsis for sidebar chat links.
    - name: The name of the chat.
    """
    return rx.text(
        name,
        size="3",
        width="220px",
        weight="medium",
        overflow="hidden",
        font_family="Inter",
        white_space="nowrap",
        text_overflow="ellipsis",
        color=rx.color(
            color="slate",
            shade=11,
        ),
        **kwargs,
    )


def msg_header(
    header_title: str,
    date: datetime.datetime | None = None,
):
    def ts_component():
        if date is None:
            return rx.box()
        return rx.moment(
            date,
            format="HH:mm:ss",
            color=rx.color(
                color="slate",
                shade=11,
            ),
            weight="medium",
        )

    return rx.hstack(
        rx.text(
            header_title,
            color=rx.color(
                color="slate",
                shade=12,
            ),
            weight="medium",
        ),
        rx.divider(
            orientation="vertical",
            color_scheme="gray",
            height="20px",
        ),
        ts_component(),
        display="flex",
        align="center",
    )
