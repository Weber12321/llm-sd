
import os
from typing import Literal, Mapping, TypedDict
from unittest.mock import Base

from lab.page.chat.agent_tools.interfaces import Agent
import streamlit as st
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from openai import BadRequestError
from utils.client.embedding import EmbeddingClient
from langgraph.types import interrupt, Command
from data.grader import GradeDocuments
from data.state import RetrivalState


class ChatCorrectiveRAGAgent(Agent):
    
    def __init__(self, config: Mapping[str, str]):
        embedding_config = config.get("embedding", {})
        if not isinstance(embedding_config, dict):
            raise ValueError("Embedding config must be a dictionary.")
        if "embedding_api_path" not in embedding_config:
            raise ValueError(
                "Embedding config must include 'embedding_api_path'.")
        self.embedding = EmbeddingClient(**embedding_config)

        vector_db_type = self.VEVTOR_DB_TYPE.get(
            config.get("vector_db", ""), ""
        )
        if not vector_db_type:
            raise ValueError("Vector DB type must be specified.")
        vector_db_config = config.get("vector_db_config", {})
        if not isinstance(vector_db_config, dict):
            raise ValueError("Vector DB config must be a dictionary.")        
        self.vector_store = self.VECTOR_DB_TYPE(**vector_db_config)

        llm_type = config.get("llm", "")
        if not llm_type:
            raise ValueError("LLM type must be specified.")
        llm_config = config.get("llm_config", {})
        if not isinstance(llm_config, dict):
            raise ValueError("LLM config must be a dictionary.")
        
        self.llm = self._init_llm(llm_type, **llm_config)
        self.graph = self._init_state_graph(RetrivalState)

        self._generate_prompt_template = ''
        self._grader_prompt_template = ''
        self._query_rewrite_prompt_template = ''

        prompt_config = config.get("prompt", {})
        if not isinstance(prompt_config, dict):
            raise ValueError("Prompt config must be a dictionary.")
        if not prompt_config:
            raise ValueError("Prompt config must be specified.")
        self._init_prompt_template(**prompt_config)
        self._init_tools()
        self._init_state_graph()
        self.agent = None

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

    def _init_prompt_template(self, **kwargs):
        self.generate_prompt_template = kwargs.get('generate_prompt', '')
        self.grader_prompt_template = kwargs.get('grader_prompt', '')
        self.query_rewrite_prompt_template = kwargs.get(
            'query_rewrite_prompt', ''
        )

    @property
    def generate_prompt_template(self):
        return self._generate_prompt_template
    
    @generate_prompt_template.setter
    def generate_prompt_template(self, template):
        return ChatPromptTemplate.from_template(template)
    
    @property
    def grader_prompt_template(self):
        return self._grader_prompt_template
    
    @grader_prompt_template.setter
    def grader_prompt_template(self, template):
        return ChatPromptTemplate.from_template(template)
    
    @property
    def query_rewrite_prompt_template(self):
        return self._query_rewrite_prompt_template

    @query_rewrite_prompt_template.setter
    def query_rewrite_prompt_template(self, template):
        return ChatPromptTemplate.from_template(template)
    
    def _init_tools(self):
        
        structured_llm_grader = self.llm.with_structured_output(
            self.GradeDocuments
        )
        
        self.retriever = self.vector_store.as_retriever()
        self.wiki_searcher = WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper()
        )

        self.grader_chain = self.grader_prompt_template | structured_llm_grader
        self.generate_chain =\
            self.generate_prompt_template | self.llm | StrOutputParser()
        self.rewrite_chain =\
            self.query_rewrite_prompt_template | self.llm | StrOutputParser()

    def retrieve(self, state):
        """
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        question = state["question"]

        # Retrieval
        documents = self.retriever.get_relevant_documents(question)
        return {"documents": documents, "question": question}

    def generate(self, state):
        """
        Generate answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """
        question = state["question"]
        documents = state["documents"]

        # RAG generation
        generation = self.rag_chain.invoke({
            "context": documents, "question": question
        })
        return {
            "documents": documents, 
            "question": question, 
            "generation": generation
        }

    def grade_documents(self, state):
        """
        Determines whether the retrieved documents are relevant to the question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates documents key with only filtered relevant documents
        """

        question = state["question"]
        documents = state["documents"]

        # Score each doc
        filtered_docs = []
        web_search = "Yes"
        for d in documents:
            score = self.grader_chain.invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score.binary_score
            if grade == "yes":
                web_search = "No"
                filtered_docs.append(d)
            else:
                continue

        if not filtered_docs:
            web_search = "Yes"
        return {
            "documents": filtered_docs, 
            "question": question, 
            "web_search": web_search
        }
    
    def transform_query(self, state):
        """
        Transform the query to produce a better question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates question key with a re-phrased question
        """

        question = state["question"]
        documents = state["documents"]

        # Re-write question
        better_question = self.rewrite_chain.invoke({"question": question})
        return {"documents": documents, "question": better_question}

    def human_approve(
        self, state
    ) -> Command[Literal["human_input", "wiki_search"]]:
        """
        Human approval for the transformed question.
        """
        is_approved = interrupt(
            {
                "task": "Is this rewrite acceptable?",
                # Surface the output that should be
                # reviewed and approved by the human.
                "question": state["question"]
            }
        )

        if is_approved:
            return Command(goto="some_node")
        else:
            return Command(goto="another_node")

    def human_input(self, state):
        """
        Human input for the transformed question.
        """
        result = interrupt(
            {
                "task": "Make any necessary edits.",
                "question": state["question"]
            }
        )

        return {
            "question": result["edited_text"]
        }

    def search(self, state):
        """
        Retrieve additional documents from the web.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates documents key with additional documents
        """

        question = state["question"]
        documents = self.wiki_searcher.run(question)

        return {"documents": documents, "question": question}

    def decide_to_generate(self, state):
        """
        Determines whether to generate an answer, or re-generate a question.

        Args:
            state (dict): The current graph state

        Returns:
            str: Binary decision for next node to call
        """

        web_search = state["web_search"]

        if web_search == "Yes":
            # All documents have been filtered check_relevance
            # We will re-generate a new query

            return "transform_query"
        else:
            # We have relevant documents, so generate answer
            return "generate"

    def init_workflow(self):

        # Define the nodes
        self.graph.add_node("retrieve", self.retrieve)
        self.graph.add_node("grade_documents", self.grade_documents)
        self.graph.add_node("generate", self.generate)
        self.graph.add_node("transform_query", self.transform_query)
        self.graph.add_node("human_approve", self.human_approve)
        self.graph.add_node("human_input", self.human_input)
        self.graph.add_node("wiki_search", self.search)

        # Buikd Graph
        self.graph.add_edge(START, "retrieve")
        self.graph.add_edge("retrieve", "grade_documents")
        self.graph.add_conditional_edges(
            "grade_documents",
            self.decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate",
            },
        )
        self.graph.add_edge("transform_query", "human_approve")
        self.graph.add_edge("human_input", "wiki_search")
        self.graph.add_edge("wiki_search", "generate")
        self.graph.add_edge("generate", END)

        # Compile
        setattr(self, "agent", self.graph.compile())

    def get_graph(self):
        if not self.agent:
            raise ValueError("Agent not initialized.")
        return self.agent.get_graph().draw_png()