from enum import Enum, auto


class Placeholder(str, Enum):
    GENERATE_TOP_P = auto()
    GENERATE_TOP_K = auto()
    GENERATE_TEMPERATURE = auto()
    GENERATE_MAX_TOKEN = auto()
    GENERATE_RESPONSE = auto()

    QUERY = auto()

    HISTORY_ANSWER = auto()
    INSTRUCTIONS = auto()
