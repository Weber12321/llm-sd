from abc import ABC, abstractmethod

from settings.configs.placeholder import Placeholder
from settings.loggers import log_io
import streamlit as st
from utils.context_key import create_context_key
from utils.session_state_registry import Registry


class Logic(ABC):

    def __call__(self, *args, response_key=None, **kwargs):
        if "key" not in kwargs:
            key = create_context_key()
        else:
            key = kwargs["key"]
        if response_key:
            Registry.register(response_key, key)
        args, kwargs = Placeholder.update_param_placeholders(*args, **kwargs)
        response = self._function(*args, **kwargs)
        st.session_state[key] = response
        return response

    @log_io
    def _function(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @abstractmethod
    def function(self, *args, **kwargs):
        """Render the template with the given arguments."""
        raise NotImplementedError
