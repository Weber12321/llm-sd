import streamlit as st
from abc import ABC, abstractmethod
from settings.loggers import log_io


class Action(ABC):

    @abstractmethod
    def function(self, *args, **kwargs):
        raise NotImplementedError
    
    @log_io
    def _function(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """define the function to be executed"""
        return self._function(*args, **kwargs)


class CallBackAction(Action):

    def __call__(self, label, button_type, *args, **kwargs):
        """Execute the function when the button is clicked"""
        is_click = st.button(
            label=label,
            type=button_type,
        )

        if is_click:
            return self._function(*args, **kwargs)
        
        return None