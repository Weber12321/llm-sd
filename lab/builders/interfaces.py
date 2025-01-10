from typing import Any
import streamlit as st

from abc import ABC, abstractmethod


class Constructor(ABC):
    
    def __init__(self):
        self.session_state = st.session_state
    
    def setup_key(self, session_name: str, name: str, value: Any):
        _temp_key = f"{session_name}_{name}"
        if not self.session_state.get(_temp_key):
            self.session_state[_temp_key] = value

    def get_key_value(self, session_name: str, name: str):
        return self.session_state[f"{session_name}_{name}"]

    def get_key_name(self, session_name: str, name: str):
        return f"{session_name}_{name}"
    
    def update_key(self, session_name: str, name: str, value: Any):
        self.session_state[f"{session_name}_{name}"] = value

    def setup_title_and_description(self, title: str, description: str):
        st.title(title)
        st.markdown(description)

    def get_session_key(self):
        return [key for key in self.session_state]

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError
    