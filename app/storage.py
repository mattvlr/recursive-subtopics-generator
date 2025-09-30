from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import current_app


class HistoryStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            entries = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        return [self._normalize_entry(entry) for entry in entries]

    def save(self, entries: List[Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    def add_entry(self, entry: Dict[str, Any]) -> None:
        entries = self.load()
        entries.insert(0, self._normalize_entry(entry))
        self.save(entries)

    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        for entry in self.load():
            if entry.get("id") == entry_id:
                return entry
        return None

    def update_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        entries = self.load()
        updated = False
        for index, entry in enumerate(entries):
            if entry.get("id") == entry_id:
                entry.update(updates)
                entries[index] = self._normalize_entry(entry)
                updated = True
                break
        if updated:
            self.save(entries)
        return updated

    def clear(self) -> None:
        self.save([])

    def _normalize_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        entry.setdefault("is_favorite", False)
        return entry


def get_store() -> HistoryStore:
    return HistoryStore(current_app.config["HISTORY_PATH"])
