import streamlit as st
from abc import ABC, abstractmethod


class Template(ABC):

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """Render the template with the given arguments."""
        raise NotImplementedError