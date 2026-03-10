from dataclasses import dataclass, field

from system.performance.modes import PerformanceMode, resolve_mode


@dataclass
class InterfaceSettings:
    position: str = "top-right"
    avatar_size: int = 96
    transparency: float = 0.85
    always_on_top: bool = True


@dataclass
class VoiceSettings:
    wake_word_enabled: bool = True
    continuous_listening: bool = True
    push_to_talk: bool = False
    microphone_name: str = "default"
    tts_voice: str = "default"
    sensitivity: float = 0.5


@dataclass
class ScreenAnalysisSettings:
    enabled: bool = True
    interval_seconds: int = 20


@dataclass
class AISettings:
    llm_model: str = "local-llm"
    vision_model: str = "local-vision"
    speech_model: str = "local-stt"
    tts_model: str = "local-tts"
    performance_mode: str = "balanced"
    use_gpu: bool = True
    memory_limit_mb: int = 2048


@dataclass
class ReplicaSettings:
    language: str = "ru"
    autostart: bool = False
    volume: float = 0.8
    interface: InterfaceSettings = field(default_factory=InterfaceSettings)
    voice: VoiceSettings = field(default_factory=VoiceSettings)
    screen: ScreenAnalysisSettings = field(default_factory=ScreenAnalysisSettings)
    ai: AISettings = field(default_factory=AISettings)

    @property
    def performance(self) -> PerformanceMode:
        return resolve_mode(self.ai.performance_mode)
