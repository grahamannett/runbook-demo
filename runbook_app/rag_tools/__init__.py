from urllib.request import urlopen

from bs4 import BeautifulSoup

from runbook_app.db_models import Document
from runbook_app.rag_tools.rag_db import load_documents_from_db, save_document_to_db
from runbook_app.rag_tools.rag_dto import DocumentDTO, StorageType, storage_type
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


def get_html_dto(url: str) -> DocumentDTO | None:
    """Fetch and save an HTML document.

    Args:
        url: URL to fetch

    Returns:
        DocumentDTO if successful, None otherwise
    """
    try:
        resp = urlopen(url)
        data = resp.read().decode("utf-8")
        soup = BeautifulSoup(data, "html.parser")

        # Extract text content
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        # Clean up title
        title = soup.title.string.replace(" ", "_").replace("/", "_").replace("\\", "_").replace("|", "_")

        return DocumentDTO(text=text, title=title, url=url)
        # save_func = save_funcs.get(storage_type)
        # if not save_func:
        #     raise ValueError(f"Invalid storage type: {storage_type}")

        # return save_func()
    except Exception as err:
        print(f"Error processing HTML document: {err}")
        return None


def load_all_documents(storage_type: StorageType = storage_type) -> list[Document]:
    """Load all documents from the configured source.

    Args:
        storage_type: Storage type ('file' or 'table')
        session: Database session (only used for 'table' storage)

        Args:
            storage_type: Storage type
            session: Database session (only used for 'table' storage)

        Returns:
            List of documents (either Document objects or dictionaries)
    """

    load_funcs = {
        StorageType.TABLE: load_documents_from_db,
        # StorageType.FILE: load_documents_from_file,
    }

    return load_funcs[storage_type]()


def save_document(document: DocumentDTO | dict, storage_type: StorageType = storage_type) -> int | None:
    text, title, url = document["text"], document["title"], document["url"]

    save_funcs = {
        StorageType.TABLE: save_document_to_db,
        # StorageType.FILE: save_document_to_file,
    }

    try:
        return save_funcs[storage_type](text=text, title=title, url=url)
    except Exception as err:
        print(f"Error saving document: {err}")
        return None


__all__ = [
    "get_html_dto",
    "save_document",
    "load_all_documents",
    "load_documents_from_db",
]


if __name__ == "__main__":
    get_html_dto("https://docs.databricks.com/en/admin/account-settings-e2/credentials.html")
