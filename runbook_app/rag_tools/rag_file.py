import json
import os
from typing import Sequence
from urllib.request import urlopen

import reflex as rx
from bs4 import BeautifulSoup
from sqlmodel import Session, select

from runbook_app.db_models import Document
from runbook_app.db_ops import with_session
from rxconstants import rag_docs_storage_type


def save_document_to_file(
    content: str,
    title: str,
    url: str,
) -> bool:
    """Save a document to a JSON file.

    Args:
        content: The document content
        title: The document title
        url: The source URL

    Returns:
        True if save was successful, False otherwise
    """
    try:
        documents = load_documents_from_file()
        documents.append({"content": content, "title": title, "url": url})

        os.makedirs("runbook-documents", exist_ok=True)
        with open("runbook-documents/documents.json", "w") as f:
            json.dump(documents, f)
        return True
    except Exception as err:
        print(f"Error saving document to file: {err}")
        return False


def load_documents_from_file() -> list[dict]:
    """Load documents from a JSON file.

    Returns:
        List of document dictionaries
    """
    try:
        if not os.path.exists("runbook-documents/documents.json"):
            return []
        with open("runbook-documents/documents.json", "r") as f:
            return json.load(f)
    except Exception as err:
        print(f"Error loading documents from file: {err}")
        return []
