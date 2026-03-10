from enum import Enum


class Emotion(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    THINKING = "thinking"
    CONFUSED = "confused"
    CURIOUS = "curious"
    CONCERNED = "concerned"
    SLEEPY = "sleepy"
