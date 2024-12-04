import os
from datetime import datetime

import pytest
import reflex as rx

from runbook_app.db_models import HTMLSource
from runbook_app.rag_tools import load_all_documents
from rxconstants import rag_docs_file_dir, rag_docs_storage_type

test_db_fixture = "test.db"


@pytest.fixture
def sample_documents():
    return [
        {
            "url": "https://example.com/doc1",
            "title": "Test_Document_1",
            "content": "This is test document 1",
            "timestamp": datetime.now().isoformat(),
        },
        {
            "url": "https://example.com/doc2",
            "title": "Test_Document_2",
            "content": "This is test document 2",
            "timestamp": datetime.now().isoformat(),
        },
    ]


@pytest.fixture
def setup_file_documents(sample_documents):
    # Save sample documents to files
    saved_paths = []
    for doc in sample_documents:
        path = _save_doc_to_file(doc["content"], doc["title"], doc["url"])
        saved_paths.append(path)

    yield

    # Cleanup: remove test files
    for path in saved_paths:
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture
def setup_db_documents(sample_documents):
    # Save sample documents to database
    saved_ids = []
    for doc in sample_documents:
        doc_id = _save_doc_to_db(doc["content"], doc["title"], doc["url"])
        saved_ids.append(doc_id)

    yield

    # Cleanup: remove test database entries
    with rx.session(url=test_db_fixture) as session:
        for doc_id in saved_ids:
            session.query(HTMLSource).filter(HTMLSource.id == doc_id).delete()
        session.commit()


def test_load_from_files(sample_documents, setup_file_documents, monkeypatch):
    # Set storage type to file
    monkeypatch.setattr("rxconstants.rag_documents", "file")

    # Load documents
    loaded_docs = load_all_documents()

    # Verify loaded documents
    assert len(loaded_docs) == len(sample_documents)
    for loaded, sample in zip(
        sorted(loaded_docs, key=lambda x: x["title"]), sorted(sample_documents, key=lambda x: x["title"])
    ):
        assert loaded["url"] == sample["url"]
        assert loaded["title"] == sample["title"]
        assert loaded["content"] == sample["content"]
        assert "timestamp" in loaded


def test_load_from_db(sample_documents, setup_db_documents, monkeypatch):
    # Set storage type to database
    monkeypatch.setattr("rxconstants.rag_documents", "table")

    # Load documents
    loaded_docs = load_all_documents()

    # Verify loaded documents
    assert len(loaded_docs) == len(sample_documents)
    for loaded, sample in zip(
        sorted(loaded_docs, key=lambda x: x["title"]), sorted(sample_documents, key=lambda x: x["title"])
    ):
        assert loaded["url"] == sample["url"]
        assert loaded["title"] == sample["title"]
        assert loaded["content"] == sample["content"]
        assert "timestamp" in loaded


@pytest.mark.skip
def test_load_with_invalid_storage_type(monkeypatch):
    # Set invalid storage type
    monkeypatch.setattr("rxconstants.rag_documents", "invalid")

    # Verify it raises KeyError
    with pytest.raises(KeyError):
        load_all_documents()
