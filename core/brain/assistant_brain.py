from __future__ import annotations
from dataclasses import dataclass
import json
import os
import glob

from core.brain.llm_adapter import LLMReply
from core.brain.llm_adapter import LLMAdapter
from core.brain.personality import PERSONALITY_PROMPT
from core.memory.memory_store import MemoryStore
from ui.emotions.state import Emotion


@dataclass
class AssistantReply:
    text: str
    emotion: Emotion
    intent: str | None
    argument: str


class AssistantBrain:
    def __init__(self, memory: MemoryStore, llm: LLMAdapter) -> None:
        self.memory = memory
        self.llm = llm
        self.memory_file = "memory_data.json"
        self.knowledge_dir = "knowledge"

        os.makedirs(self.knowledge_dir, exist_ok=True)
        self._load_long_term_memory()

    def _load_long_term_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    facts = json.load(f)
                    for fact in facts:
                        self.memory.add_long_term(fact)
            except:
                pass

    def _save_long_term_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            # Сохраняем как список, так как deque не сериализуется напрямую
            json.dump(list(self.memory.long_term), f, ensure_ascii=False, indent=4)

    def _search_knowledge_base(self, query: str) -> str:
        """Поиск по текстовым файлам в папке knowledge/"""
        found_info = []
        query_words = set(query.lower().split())

        for filepath in glob.glob(os.path.join(self.knowledge_dir, "*.txt")):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Ищем совпадения ключевых слов
                    if any(word in content.lower() for word in query_words if len(word) > 3):
                        found_info.append(f"Источник {os.path.basename(filepath)}: {content[:400]}")
            except:
                continue

        return "\n\n".join(found_info) if found_info else "Нет дополнительных данных в базе знаний."

    def build_context(self, user_text: str, screen_summary: str | None = None) -> str:
        recent = "\n".join(self.memory.recent_dialog())
        facts = "\n- ".join(self.memory.get_relevant_memory(user_text))
        knowledge = self._search_knowledge_base(user_text)

        screen_block = f"\nКонтекст экрана: {screen_summary}" if screen_summary else ""

        return (
            f"{PERSONALITY_PROMPT}\n\n"
            f"ИСТОРИЯ ДИАЛОГА:\n{recent if recent else 'нет данных'}\n\n"
            f"ЗНАНИЯ О ПОЛЬЗОВАТЕЛЕ (Факты):\n{facts if facts else 'нет данных'}\n\n"
            f"ЗНАНИЯ ИЗ БАЗЫ (Knowledge Base):\n{knowledge}\n\n"
            f"Пользователь: {user_text}"
            f"{screen_block}\n\n"
            f"Ответь строго в указанном формате."
        )

    def generate_reply(self, user_text: str, screen_summary: str | None = None) -> AssistantReply:
        context = self.build_context(user_text, screen_summary)
        raw = self.llm.generate(context).text.strip()

        emotion = Emotion.NEUTRAL
        intent = None
        argument = ""
        final_text = raw

        # --- ЛОГИКА САМООБУЧЕНИЯ ---
        if "FACT:" in raw:
            try:
                parts = raw.split("FACT:")
                final_text = parts[0].strip()
                new_fact = parts[1].split("\n")[0].strip()
                self.memory.add_long_term(new_fact)
                self._save_long_term_memory()
            except:
                pass

        # --- ПАРСИНГ ОТВЕТА ---
        try:
            lines = final_text.splitlines()
            for line in lines:
                if line.startswith("emotion:"):
                    emotion = Emotion[line.split(":", 1)[1].strip().upper()]
                elif line.startswith("intent:"):
                    val = line.split(":", 1)[1].strip()
                    intent = val if val != "none" else None
                elif line.startswith("argument:"):
                    argument = line.split(":", 1)[1].strip()
                elif line.startswith("text:"):
                    final_text = line.split(":", 1)[1].strip()
        except:
            pass

        self.memory.add_short_term(f"user: {user_text}")
        self.memory.add_short_term(f"assistant: {final_text}")

        return AssistantReply(
            text=final_text,
            emotion=emotion,
            intent=intent,
            argument=argument
        )