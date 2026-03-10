from collections import deque
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MemoryItem:
    created_at: datetime
    category: str
    text: str


class MemoryStore:
    def __init__(self, short_term_limit: int = 20, long_term_limit: int = 200) -> None:
        self.short_term = deque(maxlen=short_term_limit)
        self.long_term = deque(maxlen=long_term_limit)

    def add_short_term(self, text: str, category: str = "dialog") -> None:
        self.short_term.append(MemoryItem(datetime.utcnow(), category, text))

    def add_long_term(self, text: str, category: str = "profile") -> None:
        self.long_term.append(MemoryItem(datetime.utcnow(), category, text))

    def recent_dialog(self, limit: int = 5) -> list[str]:
        return [item.text for item in list(self.short_term)[-limit:]]
