import reflex as rx

from runbook_app.components.badges import badge_with_icon
from runbook_app.db_models import DocumentSource
from runbook_app.page_chat.chat_state import ChatState


def document_source_card(doc: DocumentSource):
    def delete_on_click():
        return ChatState.delete_doc(doc.id, str(DocumentSource.__tablename__))

    return rx.hstack(
        rx.badge(
            f"{doc.id}",
            variant="outline",
            # high_contrast=False,
            # color=rx.color("slate", 11),
        ),
        rx.vstack(
            rx.text(
                doc.title,
                weight="bold",
                overflow="hidden",
                text_overflow="ellipsis",
                color=rx.color("slate", 12),
            ),
            rx.text(
                doc.path,
                width="100%",
                overflow="hidden",
                font_family="Inter",
                white_space="nowrap",
                text_overflow="ellipsis",
                color=rx.color("slate", 11),
            ),
            rx.text(
                # description,
                width="100%",
                overflow="hidden",
                font_family="Inter",
                white_space="nowrap",
                text_overflow="ellipsis",
                color=rx.color("slate", 11),
            ),
            flex="3",
            justify="center",
            align="start",
            spacing="1",
            overflow_x="hidden",
        ),
        rx.hstack(
            rx.box(
                rx.tooltip(badge_with_icon("move-up-right"), content="refresh page"),
                on_click=rx.redirect("https://docs.databricks.com", external=True),
            ),
            rx.tooltip(badge_with_icon("file-cog"), content="edit document"),
            rx.box(
                rx.tooltip(badge_with_icon("trash-2"), content="delete document"),
                on_click=delete_on_click,
            ),
        ),
        width="100%",
        align="center",
        justify="end",
        padding="16px 12px",
        background_color=rx.color("indigo", 1),
        border=rx.color_mode_cond(
            f"1px solid {rx.color('indigo', 3)}",
            f"1px solid {rx.color('slate', 7, True)}",
        ),
        border_radius="8px",
        box_shadow="0px 1px 3px rgba(25, 33, 61, 0.1)",
    )
