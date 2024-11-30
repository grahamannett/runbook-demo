import datetime
import zoneinfo

import reflex as rx
from sqlmodel import Field


class ChatInteraction(
    rx.Model,
    table=True,
):
    """A table for questions and answers in the database."""

    prompt: str
    answer: str
    chat_participant_user_name: str
    timestamp: datetime.datetime = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/Boise"))
    chat_participant_user_avatar_url: str = "/avatar-default.png"

    chat_participant_assistant_name: str = "Reflex Bot"
    chat_participant_assistant_avatar_url: str = "/reflex-avatar.png"


class HTMLPage(rx.Model, table=True):
    """A table for storing HTML pages in the database."""

    title: str
    content: str
    url: str
    timestamp: datetime.datetime = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/Boise"))


class ParsedDocument(rx.Model, table=True):
    source: int = Field(foreign_key="htmlpage.id")
    content: str
    timestamp: datetime.datetime = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/Boise"))
