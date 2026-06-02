from __future__ import annotations

from typing import Dict, List

from .store import Event


def coalesce(events: List[Event]) -> List[Event]:
    effective: Dict[str, Event] = {}
    for ev in events:
        current = effective.get(ev.product_id)
        if current is None or ev.version > current.version:
            effective[ev.product_id] = ev
    return sorted(effective.values(), key=lambda e: e.seq)
