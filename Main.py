import time

from core.brain.assistant_brain import AssistantBrain
from core.memory.memory_store import MemoryStore
from system.config.settings import ReplicaSettings
from ui.avatar.emoji_avatar import pick_emoji


def run_demo() -> None:
    settings = ReplicaSettings()
    memory = MemoryStore(
        short_term_limit=settings.performance.max_memory_items // 4,
        long_term_limit=settings.performance.max_memory_items,
    )
    brain = AssistantBrain(memory)

    print("Replica запущена в демо-режиме.")
    print(f"Режим производительности: {settings.performance.name}")
    print("Напиши сообщение (exit для выхода).")

    while True:
        user_text = input("Ты: ").strip()
        if user_text.lower() in {"exit", "quit", "выход"}:
            print("Replica: До связи.")
            break

        reply = brain.generate_local_reply(user_text=user_text)
        avatar = pick_emoji(reply.emotion)
        print(f"{avatar} Replica: {reply.text}")

        # Имитация фонового наблюдения за экраном
        if settings.screen.enabled:
            time.sleep(min(settings.screen.interval_seconds, 1))


if __name__ == "__main__":
    run_demo()
