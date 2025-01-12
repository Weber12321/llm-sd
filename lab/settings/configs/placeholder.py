from enum import Enum, auto

from utils.session_state_registry import Registry


class Placeholder(Enum):
    GENERATE_TOP_P = auto()
    GENERATE_TOP_K = auto()
    GENERATE_TEMPERATURE = auto()
    GENERATE_MAX_TOKEN = auto()
    GENERATE_RESPONSE = auto()

    QUERY = auto()

    HISTORY_ANSWER = auto()
    INSTRUCTIONS = auto()

    @classmethod
    def update_param_placeholders(cls, *args, **kwargs):
        new_args = [Registry.get(arg) if isinstance(arg, cls) else arg for arg in args]
        new_kwargs = {
            k: Registry.get(v) if isinstance(v, cls) else v for k, v in kwargs.items()
        }
        return new_args, new_kwargs
