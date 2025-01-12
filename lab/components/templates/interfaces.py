import inspect
import os
from abc import ABC, abstractmethod

from settings.configs.placeholder import Placeholder
from utils.session_state_registry import Registry


class Template(ABC):

    def __call__(self, *args, response_key=None, **kwargs):
        key = self.generate_key()
        kwargs["key"] = key
        if response_key:
            Registry.register(response_key, key)
        for i, arg in enumerate(args):
            if isinstance(arg, Placeholder):
                args[i] = Registry.get(arg)
        for k, v in kwargs.items():
            if isinstance(v, Placeholder):
                kwargs[k] = Registry.get(v)
        return self.element(*args, **kwargs)

    @classmethod
    def generate_key(self):
        stack = inspect.stack()[2:]
        frames = []
        for frame_info in stack:
            lineno = frame_info.lineno
            file_name = os.path.basename(frame_info.filename)
            frames.append(f"{file_name}:{lineno}")

        key = "|".join(frames)
        return key

    @abstractmethod
    def element(self, *args, **kwargs):
        """Render the template with the given arguments."""
        raise NotImplementedError
