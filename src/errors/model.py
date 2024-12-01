from enum import Enum


class ModelError(Enum):
    NO_API_KEY = "model - could not find GROQ_API_KEY in environment. aborting..."
    INVALID_API_KEY = "model - an invalid api key was provided. Check your .env."
