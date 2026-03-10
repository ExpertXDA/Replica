from dataclasses import dataclass

from core.brain.personality import PERSONALITY_PROMPT
from core.memory.memory_store import MemoryStore
from ui.emotions.state import Emotion


@dataclass
class AssistantReply:
    text: str
    emotion: Emotion


class AssistantBrain:
    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory

    def build_context(self, user_text: str, screen_summary: str | None = None) -> str:
        recent = "\n".join(self.memory.recent_dialog())
        screen_block = f"\nКонтекст экрана: {screen_summary}" if screen_summary else ""
        return (
            f"{PERSONALITY_PROMPT}\n\n"
            f"Последний диалог:\n{recent if recent else 'нет данных'}"
            f"\n\nЗапрос пользователя: {user_text}{screen_block}"
        )

    def generate_local_reply(self, user_text: str, screen_summary: str | None = None) -> AssistantReply:
        normalized = user_text.lower()
        if "ошиб" in normalized or "не работает" in normalized:
            emotion = Emotion.CONCERNED
            reply = "Похоже что-то пошло не так. Хочешь, разберём это шаг за шагом?"
        elif "спасибо" in normalized:
            emotion = Emotion.HAPPY
            reply = "Рад помочь. Если нужно, продолжим."
        elif "?" in user_text:
            emotion = Emotion.THINKING
            reply = "Интересный вопрос. Сейчас разложу по пунктам."
        else:
            emotion = Emotion.NEUTRAL
            reply = "Понял тебя. Продолжаю наблюдать и помогать по ходу."

        if screen_summary and "много вкладок" in screen_summary.lower():
            reply += " Вижу много открытых вкладок, можем навести порядок."
            emotion = Emotion.CURIOUS

        self.memory.add_short_term(f"user: {user_text}")
        self.memory.add_short_term(f"assistant: {reply}")
        return AssistantReply(text=reply, emotion=emotion)
