from abc import ABC, abstractmethod

from settings.configs.placeholder import Placeholder
from utils.context_key import create_context_key
from utils.session_state_registry import Registry


class Template(ABC):

    def __call__(self, *args, response_key=None, **kwargs):
        if "key" not in kwargs:
            key = create_context_key()
            kwargs["key"] = key
        if response_key:
            Registry.register(response_key, key)
        args, kwargs = Placeholder.update_param_placeholders(*args, **kwargs)
        return self.element(*args, **kwargs)

    @abstractmethod
    def element(self, *args, **kwargs):
        """Render the template with the given arguments."""
        raise NotImplementedError
