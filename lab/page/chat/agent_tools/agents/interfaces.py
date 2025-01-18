

from abc import ABC, abstractmethod
from typing import Type
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_openai import ChatOpenAI, OpenAI
from langgraph.graph import StateGraph


class Agent(ABC):

    LLM_TYPE = {
        "open_ai": OpenAI,
        "chat_open_ai": ChatOpenAI
    }

    VECTOR_DB_TYPE = {
        "opensearch": OpenSearchVectorSearch,
    }

    @abstractmethod
    def _init_state_graph(self, state_class: Type):
        return setattr(
            self, "state", StateGraph(state_class)
        )
    
    @abstractmethod
    def _init_llm(self, llm_type, **kwargs):
        if not llm_type.startswith("chat_"):
            raise ValueError(
                "llm_type must start with 'chat_'"
            )
        try:
            return self.LLM_TYPE[llm_type](**kwargs)
        except KeyError as exc:
            raise ValueError(
                f"LLM type {llm_type} not found "
                f"in {self.LLM_TYPE.keys()}."
            ) from exc
    
    @abstractmethod
    def _init_prompt_template(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _init_tools(self):
        # Initialize the tools
        raise NotImplementedError

    @abstractmethod
    def init_workflow(self):
        # Initialize the workflow
        raise NotImplementedError