from __future__ import annotations

from pathlib import Path

from ui.avatar.emoji_avatar import pick_emoji
from ui.emotions.state import Emotion


class AvatarProvider:
    def __init__(self, avatars_dir: str = "assets/avatars") -> None:
        self.avatars_dir = Path(avatars_dir)
        self.avatars_dir.mkdir(parents=True, exist_ok=True)

    def get_avatar_image_path(self, emotion: Emotion) -> str | None:
        for ext in ("png", "jpg", "jpeg", "webp"):
            candidate = self.avatars_dir / f"{emotion.value}.{ext}"
            if candidate.exists():
                return str(candidate)
        return None

    def get_fallback_emoji(self, emotion: Emotion) -> str:
        return pick_emoji(emotion)
