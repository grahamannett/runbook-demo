import json
from datetime import datetime
from urllib.request import urlopen

import reflex as rx

from runbook_app.page_chat.chat_messages.model_chat_interaction import HTMLPage
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


def _save_doc_to_db(data: str, title: str, url: str) -> str:
    with rx.session() as session:
        page = HTMLPage(title=title, content=data, url=url)
        session.add(page)
        session.commit()
    return page.id


_save_types = {"table": _save_doc_to_db, "file": _save_doc_to_file}


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
