from collections import deque
from dataclasses import dataclass
from datetime import datetime
import re


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

    def add_long_term(self, text: str, category: str = "fact") -> None:
        # Убираем дубликаты, если факт уже есть
        if text not in [item.text for item in self.long_term]:
            self.long_term.append(MemoryItem(datetime.utcnow(), category, text))

    def get_relevant_memory(self, query: str, limit: int = 3) -> list[str]:
        """Ищем факты, которые подходят под запрос пользователя"""
        query_words = set(re.findall(r'\w+', query.lower()))
        relevant = []

        for item in reversed(self.long_term):  # Ищем с конца (самое свежее)
            item_words = set(re.findall(r'\w+', item.text.lower()))
            # Если пересечение слов больше 1 (или другое условие)
            if query_words.intersection(item_words):
                relevant.append(item.text)
            if len(relevant) >= limit: break

        return relevant

    def recent_dialog(self, limit: int = 5) -> list[str]:
        return [item.text for item in list(self.short_term)[-limit:]]