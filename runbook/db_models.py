from datetime import datetime
from enum import StrEnum, auto

import reflex as rx
from sqlmodel import JSON, Column, Field

from rxconstants import tz


class Runbook(rx.Model, table=True):
    """A table for storing runbooks in the database."""

    created_by: str
    title: str = ""
    description: str = ""

    status: str = "active"  # active, archived, draft, exported
    created_at: datetime = datetime.now(tz=tz)

    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(tz=tz),
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(tz=tz),
        },
    )


class ChatInteraction(rx.Model, table=True):
    """A table for questions and answers in the database."""

    prompt: str
    answer: str
    timestamp: datetime = datetime.now(tz=tz)  # Field(default_factory=lambda: datetime.now(tz=tz))

    # Relationship to runbook
    interaction_id: int | None = Field(foreign_key="runbook.id")

    chat_participant_user_name: str
    chat_participant_assistant_name: str = "runbook"

    # avatars - just ignore this for now
    chat_participant_user_avatar_url: str = "/user-avatar.png"
    chat_participant_assistant_avatar_url: str = "/runbook-avatar.png"


class ContentType(StrEnum):
    HTML = auto()
    TEXT = auto()
    JSON = auto()
    # default
    DEFAULT = HTML


class DocumentBase(rx.Model):
    # soft delete fields
    is_deleted: bool = Field(default=False)
    deleted_at: datetime | None = Field(default=None)

    #
    created_at: datetime = datetime.now(tz=tz)
    updated_at: datetime = datetime.now(tz=tz)


class DocumentSource(DocumentBase, table=True):
    """A table for storing HTML pages in the database."""

    path: str
    content: str  # either the raw html or the parsed html content
    parsed_content: str | None = ""
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))

    title: str | None = None
    content_type: ContentType = ContentType.DEFAULT

    def __repr__(self):
        return f"DocSrc(urls={self.path}, title={self.title}, content_type={self.content_type})"


DocumentTableLookup = {
    "documentsource": DocumentSource,
}

TableLookup = {
    "runbook": Runbook,
    "chatinteraction": ChatInteraction,
    **DocumentTableLookup,
}
