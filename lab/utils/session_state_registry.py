import streamlit as st

class Registry:
    if "_mapping" not in st.session_state:
        st.session_state["_mapping"] = {}
    _mapping = st.session_state["_mapping"]

    @classmethod
    def register(cls, key, value):
        cls._mapping.update({key: value})

    @classmethod
    def get(cls, key):
        return st.session_state.get(cls._mapping.get(key))
