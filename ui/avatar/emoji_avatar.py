from ui.emotions.state import Emotion


EMOJI_BY_EMOTION = {
    Emotion.NEUTRAL: "😐",
    Emotion.HAPPY: "🙂",
    Emotion.THINKING: "🤔",
    Emotion.CONFUSED: "😕",
    Emotion.CURIOUS: "😲",
    Emotion.CONCERNED: "😟",
    Emotion.SLEEPY: "😴",
}


def pick_emoji(emotion: Emotion) -> str:
    return EMOJI_BY_EMOTION.get(emotion, "😐")
