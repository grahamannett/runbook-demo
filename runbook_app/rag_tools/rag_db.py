from sqlmodel import Session, select

from runbook_app.db_models import Document, DocumentSource
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
        page = Document(content=content, title=title, path=url)
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
def load_sources_from_db(*, session: Session, filter_url: str | None = None) -> list[DocumentSource]:
    try:
        query = select(DocumentSource)

        if filter_url:
            query = query.where(DocumentSource.path.contains(filter_url))

        return list(session.exec(query).all())
    except Exception as err:
        print(f"Error loading sources from db: {err}")
        return []


@with_session
def document_exists_in_db(url: str, *, session: Session) -> bool:
    try:
        query = select(DocumentSource).where(
            DocumentSource.path == url,
            DocumentSource.is_deleted == False,
        )
        return session.exec(query).one_or_none() is not None
    except Exception as err:
        print(f"Error checking document existence in db: {err}")
        return False
