from datetime import datetime
from typing import Sequence

import reflex as rx
from sqlmodel import column, func, or_, select

from runbook_app.db_models import ChatInteraction, Document, Runbook

MAX_QUESTIONS = 10


def get_latest_runbook(username: str) -> Runbook | None:
    with rx.session() as session:
        # Try to find the latest active runbook for the current user
        query = select(Runbook).where(Runbook.created_by == username).order_by(Runbook.created_at.desc())
        runbook = session.exec(query).first()
        return runbook


def get_runbooks(username: str) -> Sequence[Runbook]:
    with rx.session() as session:
        # Try to find the latest active runbook for the current user
        query = select(Runbook).where(Runbook.created_by == username).order_by(Runbook.created_at.desc())
        runbooks = session.exec(query).all()
        return runbooks


def create_new_runbook(username: str) -> Runbook:
    with rx.session() as session:
        runbook = Runbook(
            created_by=username,
            status="active",
        )
        session.add(runbook)
        session.flush()  # This assigns an ID to the runbook
        runbook.title = f"Runbook {runbook.id}"
        session.commit()
        session.refresh(runbook)
        return runbook


def fetch_messages(username: str, prompt: str, filter_str: str | None = None, limit: int = MAX_QUESTIONS):
    with rx.session() as session:
        query = select(ChatInteraction).where(ChatInteraction.chat_participant_user_name == username)

        if filter_str:
            query = query.where(
                or_(
                    column(ChatInteraction.prompt).ilike(f"%{filter_str}%"),
                    column(ChatInteraction.answer).ilike(f"%{filter_str}%"),
                ),
            )

        query = query.order_by(ChatInteraction.timestamp.desc())
        if limit:
            query = query.limit(limit)

        return session.exec(query).all()


def get_runbook_chat_interactions(runbook_id: int) -> Sequence[ChatInteraction]:
    with rx.session() as session:
        query = select(ChatInteraction).where(ChatInteraction.interaction_id == runbook_id)
        return session.exec(query).all()
