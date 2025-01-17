

from abc import ABC, abstractmethod
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_openai import ChatOpenAI, OpenAI


class Agent(ABC):

    LLM_TYPE = {
        "open_ai": OpenAI,
        "chat_open_ai": ChatOpenAI
    }

    VECTOR_DB_TYPE = {
        "opensearch": OpenSearchVectorSearch,
    }

    @abstractmethod
    def _init_state_graph(self):
        # Initialize the state graph
        raise NotImplementedError
    
    @abstractmethod
    def _init_llm(self):
        # Initialize the LLM
        raise NotImplementedError
    
    @abstractmethod
    def _init_tools(self):
        # Initialize the tools
        raise NotImplementedError

    @abstractmethod
    def init_workflow(self):
        # Initialize the workflow
        raise NotImplementedError