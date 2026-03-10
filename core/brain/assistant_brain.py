from dataclasses import dataclass

from core.brain.llm_adapter import LLMAdapter
from core.brain.personality import PERSONALITY_PROMPT
from core.memory.memory_store import MemoryStore
from ui.emotions.state import Emotion


@dataclass
class AssistantReply:
    text: str
    emotion: Emotion


class AssistantBrain:
    def __init__(self, memory: MemoryStore, llm: LLMAdapter) -> None:
        self.memory = memory
        self.llm = llm

    def build_context(self, user_text: str, screen_summary: str | None = None) -> str:
        recent = "\n".join(self.memory.recent_dialog())
        screen_block = f"\nКонтекст экрана: {screen_summary}" if screen_summary else ""
        return (
            f"{PERSONALITY_PROMPT}\n\n"
            f"Последний диалог:\n{recent if recent else 'нет данных'}"
            f"\n\nЗапрос пользователя: {user_text}{screen_block}"
        )

    def generate_reply(self, user_text: str, screen_summary: str | None = None) -> AssistantReply:
        context = self.build_context(user_text, screen_summary)
        llm_reply = self.llm.generate(context).text.strip()
        if not llm_reply:
            llm_reply = "Дай секунду, подумаю над этим."

        normalized = user_text.lower()
        if "ошиб" in normalized or "не работает" in normalized:
            emotion = Emotion.CONCERNED
        elif "спасибо" in normalized:
            emotion = Emotion.HAPPY
        elif "?" in user_text:
            emotion = Emotion.THINKING
        elif screen_summary and "изменения" in screen_summary.lower():
            emotion = Emotion.CURIOUS
        else:
            emotion = Emotion.NEUTRAL

        self.memory.add_short_term(f"user: {user_text}")
        self.memory.add_short_term(f"assistant: {llm_reply}")
        return AssistantReply(text=llm_reply, emotion=emotion)
