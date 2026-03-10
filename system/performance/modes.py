from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceMode:
    name: str
    screen_interval_seconds: int
    max_memory_items: int
    model_profile: str


ECO = PerformanceMode(
    name="eco",
    screen_interval_seconds=60,
    max_memory_items=30,
    model_profile="small",
)

BALANCED = PerformanceMode(
    name="balanced",
    screen_interval_seconds=20,
    max_memory_items=80,
    model_profile="medium",
)

MAX = PerformanceMode(
    name="max",
    screen_interval_seconds=10,
    max_memory_items=200,
    model_profile="large",
)


def resolve_mode(mode_name: str) -> PerformanceMode:
    modes = {"eco": ECO, "balanced": BALANCED, "max": MAX}
    return modes.get(mode_name.lower(), BALANCED)
