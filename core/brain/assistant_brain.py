from dataclasses import dataclass

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

    def build_context(self, user_text: str, screen_summary: str | None = None) -> str:

        recent = "\n".join(self.memory.recent_dialog())

        screen_block = ""
        if screen_summary:
            screen_block = f"\nКонтекст экрана: {screen_summary}"

        return (
            f"{PERSONALITY_PROMPT}\n\n"
            f"Недавний диалог:\n"
            f"{recent if recent else 'нет данных'}\n\n"
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
        text = raw

        try:

            lines = raw.splitlines()

            for line in lines:

                if line.startswith("emotion:"):
                    emotion_str = line.split(":", 1)[1].strip()
                    emotion = Emotion[emotion_str.upper()]

                elif line.startswith("intent:"):
                    intent_value = line.split(":", 1)[1].strip()
                    if intent_value != "none":
                        intent = intent_value

                elif line.startswith("argument:"):
                    argument = line.split(":", 1)[1].strip()

                elif line.startswith("text:"):
                    text = line.split(":", 1)[1].strip()

        except Exception:
            text = raw

        self.memory.add_short_term(f"user: {user_text}")
        self.memory.add_short_term(f"assistant: {text}")

        return AssistantReply(
            text=text,
            emotion=emotion,
            intent=intent,
            argument=argument
        )