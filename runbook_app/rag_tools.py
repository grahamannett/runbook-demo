import json
import os
from datetime import datetime
from urllib.request import urlopen

import reflex as rx

from runbook_app.db_models import HTMLSource
from rxconstants import rag_documents, saved_rag_documents


def _save_doc_to_file(data: str, title: str, url: str) -> str:
    filepath = f"{saved_rag_documents}/{title}.json"

    outfile = {
        "url": url,
        "title": title,
        "content": data,
        "timestamp": datetime.now().isoformat(),
    }
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json.dumps(outfile, indent=4))

    return filepath


def _save_doc_to_db(data: str, title: str, url: str, db_url: str | None = None) -> int | None:
    with rx.session(url=db_url) as session:
        page = HTMLSource(title=title, content=data, url=url)
        session.add(page)
        session.commit()
        return page.id


_save_types = {"table": _save_doc_to_db, "file": _save_doc_to_file}


def _load_docs_from_file() -> list[dict]:
    documents = []
    try:
        for filename in os.listdir(saved_rag_documents):
            if filename.endswith(".json"):
                filepath = os.path.join(saved_rag_documents, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    doc = json.load(f)
                    documents.append(doc)
    except Exception as err:
        print("!!ERROR LOADING DOCUMENTS FROM FILE!!")
        print(f"Error loading documents from files: {str(err)}")
    return documents


def _load_docs_from_db(db_url: str | None = None) -> list[dict]:
    documents = []
    try:
        with rx.session(url=db_url) as session:
            pages = session.query(HTMLSource).all()
            for page in pages:
                doc = {
                    "url": page.url,
                    "title": page.title,
                    "content": page.content,
                    "timestamp": page.created_at.isoformat() if page.created_at else None,
                }
                documents.append(doc)
    except Exception as err:
        print(f"Error loading documents from database: {str(err)}")
    return documents


_load_types = {"table": _load_docs_from_db, "file": _load_docs_from_file}


def load_all_documents() -> list[dict]:
    """Load all documents from the configured source (file or database)."""
    load_func = _load_types[rag_documents]
    return load_func()


def get_html_document(url: str) -> bool:
    try:
        resp = urlopen(url)
        data = resp.read().decode("utf-8")

        title = data[data.find("<title>") + 7 : data.find("</title>")]
        title = (
            title.replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
            .replace("*", "_")
            .replace("?", "_")
            .replace('"', "_")
            .replace("<", "_")
            .replace(">", "_")
            .replace("|", "_")
        )

        save_func = _save_types[rag_documents]
        save_resp = save_func(data, title, url)
        return save_resp

    except Exception as err:
        print(f"Error fetching document: {str(err)}")
        return False


if __name__ == "__main__":
    get_html_document("https://docs.databricks.com/en/admin/account-settings-e2/credentials.html")
