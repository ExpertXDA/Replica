from __future__ import annotations

import json
from pathlib import Path

from system.config.settings import AISettings, InterfaceSettings, ReplicaSettings, ScreenAnalysisSettings, VoiceSettings


DEFAULT_SETTINGS_PATH = Path("config/settings.json")


def load_settings(path: Path = DEFAULT_SETTINGS_PATH) -> ReplicaSettings:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        default = ReplicaSettings()
        save_settings(default, path)
        return default

    data = json.loads(path.read_text(encoding="utf-8"))
    return ReplicaSettings(
        language=data.get("language", "ru"),
        autostart=data.get("autostart", False),
        volume=data.get("volume", 0.8),
        interface=InterfaceSettings(**data.get("interface", {})),
        voice=VoiceSettings(**data.get("voice", {})),
        screen=ScreenAnalysisSettings(**data.get("screen", {})),
        ai=AISettings(**data.get("ai", {})),
    )


def save_settings(settings: ReplicaSettings, path: Path = DEFAULT_SETTINGS_PATH) -> None:
    payload = {
        "language": settings.language,
        "autostart": settings.autostart,
        "volume": settings.volume,
        "interface": settings.interface.__dict__,
        "voice": settings.voice.__dict__,
        "screen": settings.screen.__dict__,
        "ai": settings.ai.__dict__,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
