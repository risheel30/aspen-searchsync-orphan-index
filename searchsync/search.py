from __future__ import annotations

from typing import List

from . import store


def matches(doc: dict, query: str) -> bool:
    if not query:
        return True
    q = query.lower()
    if q in doc.get("name", "").lower():
        return True
    if q in doc.get("description", "").lower():
        return True
    return any(q in str(t).lower() for t in doc.get("tags", []))


def run_search(query: str = "", tag: str = "") -> List[dict]:
    hits = []
    for doc in store.search_index.values():
        if not matches(doc, query):
            continue
        if tag:
            doc_tags = [str(t).lower() for t in doc.get("tags", [])]
            if tag.lower() not in doc_tags:
                continue
        hits.append(doc)
    hits.sort(key=lambda d: d["id"])
    return hits
