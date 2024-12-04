from sqlmodel import Session, select

from runbook_app.db_models import Document
from runbook_app.db_ops import with_session


@with_session
def save_document_to_db(
    content: str,
    title: str,
    url: str,
    *,
    session: Session,
) -> int:
    """Save a document to the database.

    Args:
        content: The document content
        title: The document title
        url: The source URL
        session: Database session

    Returns:
        The ID of the saved document

    Raises:
        SQLAlchemyError: If there's an error saving to the database
    """
    try:
        page = Document(content=content, title=title, url=url)
        session.add(page)
        session.commit()
        session.refresh(page)
        return page.id
    except Exception as err:
        print(f"Error saving document to db: {err}")
        session.rollback()
        raise err


@with_session
def load_documents_from_db(*, session: Session) -> list[Document]:
    """Load all documents from the database.

    Args:
        session: Database session

    Returns:
        List of Document objects
    """
    try:
        return list(session.exec(select(Document)).all())
    except Exception as err:
        print(f"Error loading documents from db: {err}")
        return []


@with_session
def document_exists_in_db(url: str, *, session: Session) -> bool:
    try:
        return session.exec(select(Document).where(Document.url == url)).one_or_none() is not None
    except Exception as err:
        print(f"Error checking document existence in db: {err}")
        return False