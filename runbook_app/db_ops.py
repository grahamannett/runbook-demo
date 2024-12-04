from functools import wraps
from typing import Callable, ParamSpec, Sequence, TypeVar

import reflex as rx
from sqlmodel import Session, column, func, or_, select
from sqlmodel.sql.expression import SelectOfScalar

from runbook_app.db_models import ChatInteraction, Document, Runbook
from rxconstants import MAX_QUESTIONS

Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")


def with_session(fn: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
    """Decorator that handles session management for database operations.

    If a session is provided in the kwargs, it will be used. Otherwise, a new session
    will be created and passed to the function.

    Args:
        fn: The database operation function to wrap. Function should accept a session
            keyword argument of type Session.

    Returns:
        A wrapped function that handles session management
    """

    @wraps(fn)
    def wrapper(*args, **kwargs) -> ReturnType:
        session = kwargs.get("session")
        if session is not None:
            return fn(*args, **kwargs)
        else:
            with rx.session() as new_session:
                return fn(*args, **kwargs, session=new_session)

    return wrapper


# Runbook Operations
@with_session
def get_latest_runbook(username: str, *, session: Session) -> Runbook | None:
    """Get the most recent runbook for a user.

    Args:
        username: The user to get the runbook for
        session: The database session to use

    Returns:
        The most recent runbook or None if no runbooks exist
    """
    query: SelectOfScalar[Runbook] = (
        select(Runbook).where(Runbook.created_by == username).order_by(Runbook.created_at.desc())
    )
    return session.exec(query).first()


@with_session
def get_runbooks(username: str, *, session: Session) -> list[Runbook]:  # type: ignore
    """Get all runbooks for a user, ordered by creation date.

    Args:
        username: The user to get runbooks for
        session: The database session to use

    Returns:
        A sequence of runbooks ordered by creation date descending
    """
    query = select(Runbook).where(Runbook.created_by == username).order_by(Runbook.created_at.desc())
    return list(session.exec(query).all())


@with_session
def create_new_runbook(username: str, *, session: Session) -> Runbook:
    """Create a new runbook for a user.

    Args:
        username: The user to create the runbook for
        session: The database session to use

    Returns:
        The newly created runbook

    Raises:
        SQLAlchemyError: If there's an error creating the runbook
    """
    try:
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
    except Exception as e:
        session.rollback()
        raise


# Chat Interaction Operations
@with_session
def fetch_messages(
    username: str,
    prompt: str,
    *,
    session: Session,
    filter_str: str | None = None,
    limit: int = MAX_QUESTIONS,
) -> Sequence[ChatInteraction]:
    """Fetch chat messages for a user with optional filtering.

    Args:
        username: The user to fetch messages for
        prompt: The prompt to search for
        session: The database session to use
        filter_str: Optional string to filter messages by
        limit: Maximum number of messages to return

    Returns:
        A sequence of chat interactions ordered by timestamp descending
    """
    query: SelectOfScalar[ChatInteraction] = select(ChatInteraction).where(
        ChatInteraction.chat_participant_user_name == username
    )

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


@with_session
def get_runbook_chat_interactions(
    runbook_id: int,
    *,
    session: Session,
) -> list[ChatInteraction]:
    """Get all chat interactions for a specific runbook.

    Args:
        runbook_id: The ID of the runbook to get interactions for
        session: The database session to use

    Returns:
        A sequence of chat interactions for the runbook
    """
    query: SelectOfScalar[ChatInteraction] = select(ChatInteraction).where(ChatInteraction.interaction_id == runbook_id)
    return list(session.exec(query).all())


@with_session
def save_chat_interaction(
    chat_interaction: ChatInteraction,
    *,
    session: Session,
) -> ChatInteraction:
    """Save a new chat interaction to the database.

    Args:
        chat_interaction: The chat interaction to save
        session: The database session to use

    Returns:
        The saved chat interaction with updated database fields

    Raises:
        SQLAlchemyError: If there's an error saving the interaction
    """
    try:
        session.add(chat_interaction)
        session.commit()
        session.refresh(chat_interaction)
        return chat_interaction
    except Exception as err:
        print(f"Warning, error saving chat interaction: {err}\n{chat_interaction=}")
        session.rollback()
        raise


@with_session
def check_chat_interaction_exists(
    username: str,
    prompt: str,
    runbook_id: int,
    *,
    session: Session,
) -> bool:
    """Check if a specific chat interaction already exists.

    Args:
        username: The user who made the interaction
        prompt: The prompt to check for
        runbook_id: The ID of the runbook to check in
        session: The database session to use

    Returns:
        True if the interaction exists, False otherwise
    """
    query: SelectOfScalar[ChatInteraction] = (
        select(ChatInteraction)
        .where(ChatInteraction.chat_participant_user_name == username)
        .where(ChatInteraction.prompt == prompt)
        .where(ChatInteraction.interaction_id == runbook_id)
    )

    return session.exec(query).one_or_none() is not None
