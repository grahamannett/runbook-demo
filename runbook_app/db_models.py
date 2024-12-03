from datetime import datetime

import reflex as rx
from sqlmodel import Field

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


class ChatInteraction(
    rx.Model,
    table=True,
):
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


class HTMLSource(rx.Model, table=True):
    """A table for storing HTML pages in the database."""

    title: str
    content: str
    url: str
    created_at: datetime = datetime.now(tz=tz)


class Document(rx.Model, table=True):
    """A table for storing parsed documents."""

    content: str = ""
    filepath: str | None = None

    source: int | None = Field(foreign_key="htmlsource.id")
    created_at: datetime = datetime.now(tz=tz)
