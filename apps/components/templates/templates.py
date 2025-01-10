from typing import List
import streamlit as st
from components.templates.interfaces import Template


class TextInputTemplate(Template):
    def __call__(self, label, placeholder, **kwargs) -> str:
        """
        Construct a text input with the given label and value.
        """
        return st.text_input(label, placeholder, **kwargs)


class TextPromptTemplate(Template):

    def __call__(self, label, value, height=300, **kwargs) -> str:
        """
        Construct a text area with the given label and value.
        """
        return st.text_area(label, value, height, **kwargs)


class NumberParameterTemplate(Template):

    def __call__(
        self, 
        label, 
        value, 
        min_value=0,
        max_value=100,
        step=1,
        **kwargs
    ) -> int | float:
        """
        Construct a number input slider with the given label and value.
        """
        return st.slider(
            label=label,
            value=value,
            min_value=min_value,
            max_value=max_value,
            step=step,
            **kwargs
        )


class ResponseTemplate(Template):

    def __call__(self, label, key, height, **kwargs) -> None:
        """
        Construct a text area with the given label and key for response.
        """
        text_area_container = st.empty()
        text_area_container.text_area(
            label=label,
            key=key,
            height=height,
            **kwargs
        )


class SelectBarTemplate(Template):

    def __call__(
        self, 
        label: str, 
        options: List[str], 
        value: List[str], 
        **kwargs
    ) -> List[str]:
        """
        Construct a select bar with the given label and options.
        """
        return st.multiselect(
            label, options, value, **kwargs
        )