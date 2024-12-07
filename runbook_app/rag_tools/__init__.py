from urllib.request import urlopen

from bs4 import BeautifulSoup

from runbook_app.db_models import ContentType, Document, DocumentSource
from runbook_app.rag_tools.rag_db import (
    document_exists_in_db,
    load_documents_from_db,
    load_sources_from_db,
    save_document_to_db,
)
from runbook_app.rag_tools.rag_dto import StorageType, storage_type
from runbook_app.rag_tools.rag_file import load_documents_from_file, save_document_to_file


def _check_storage_type():
    if storage_type == StorageType.FILE:
        raise NotImplementedError("File storage not implemented yet")


_check_storage_type()


def valid_url(url: str) -> bool:
    if not url.startswith(("http://", "https://")):
        return False
    try:
        from urllib.parse import urlparse

        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_source(url: str, content_type: ContentType = ContentType.DEFAULT) -> DocumentSource | None:
    """Fetch and save an HTML document.

    Args:
        url: URL to fetch

    Returns:
        DocumentSource if successful, None otherwise
    """

    def text_from_html(s):
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)
        return text

    def clean_title(s):
        # Clean up title
        return s.title.string.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("|", "_")

    try:
        resp = urlopen(url)
        data = resp.read().decode("utf-8")

        soup = BeautifulSoup(data, "html.parser")

        # Extract text content
        for script in soup(["script", "style"]):
            script.decompose()

        title = soup.title.string

        return DocumentSource(path=url, title=title, content=data, content_type=content_type)
    except Exception as err:
        print(f"Error processing HTML document: {err}")
        return None


def load_all_documents(storage_type: StorageType = storage_type, **kwargs) -> list[Document]:
    """Load all documents from the configured source.

    Args:
        storage_type: Storage type ('file' or 'table')
        session: Database session (only used for 'table' storage)

        Args:
            storage_type: Storage type
            session: Database session (only used for 'table' storage)

        Returns:
            Callable that loads all documents
    """

    load_funcs = {
        StorageType.TABLE: load_documents_from_db,
        # StorageType.FILE: load_documents_from_file,
    }

    return load_funcs[storage_type](**kwargs)


def save_document(
    document: dict,
    storage_type: StorageType = storage_type,
    **kwargs,
) -> int | None:
    text, title, url = document["text"], document["title"], document["url"]

    save_funcs = {
        StorageType.TABLE: save_document_to_db,
        # StorageType.FILE: save_document_to_file,
    }

    try:
        return save_funcs[storage_type](text=text, title=title, url=url, **kwargs)
    except Exception as err:
        print(f"Error saving document: {err}")
        return None


def document_exists(url: str, **kwargs) -> bool:
    """Check if a document exists in the database."""
    return document_exists_in_db(url, **kwargs)


__all__ = [
    "get_source",
    "save_document",
    "document_exists",
    "load_all_documents",
    "load_sources_from_db",
    "load_documents_from_db",
]


if __name__ == "__main__":
    get_source("https://docs.databricks.com/en/admin/account-settings-e2/credentials.html")
