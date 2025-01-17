
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


class ChatCorrectiveRAGAgent(Agent):

    class GradeDocuments(BaseModel):
        """Binary score for relevance check on retrieved documents."""
        binary_score: str = Field(
            description="Documents are relevant to the question, 'yes' or 'no'"
        )

    class State(TypedDict):
        """
        Represents the state of our graph.

        Attributes:
            question: question
            generation: LLM generation
            web_search: whether to add search
            documents: list of documents
            rewrite_question: rephrased question
            rewrite_generation: LLM generation
            rewrite_documents: list of documents
        """
        question: str
        generation: str
        web_search: str
        documents: list[str]

    def __init__(self, config: Mapping[str, str]):
        self._embedding = None
        self._llm = None
        self._vector_store = None
        self._generate_prompt_template = ''
        self._grader_prompt_template = ''
        self._query_rewrite_prompt_template = ''
        self._init_state_graph()
        self._init_tools(**config)

    @property
    def embedding(self):
        return self._embedding
    
    @embedding.setter
    def embedding(self, **kwargs):
        return EmbeddingClient(**kwargs)

    @property
    def vector_store(self):
        return self._vector_store
    
    @vector_store.setter
    def vector_store(self, vector_db_type, **kwargs):
        try:
            self._vector_store = self.VECTOR_DB_TYPE[
                vector_db_type](**kwargs)
        except KeyError as exc:
            raise ValueError(
                f"Vector DB type {vector_db_type} not found "
                f"in {self.VECTOR_DB_TYPE.keys()}."
            ) from exc

    @property
    def llm(self):
        return self._llm
    
    @llm.setter
    def llm(self, llm_type, **kwargs):
        if not llm_type.startswith("chat_"):
            raise ValueError(
                "llm_type must start with 'chat_'"
            )
        try:
            self._llm = self.LLM_TYPE[llm_type](**kwargs)
        except KeyError as exc:
            raise ValueError(
                f"LLM type {llm_type} not found "
                f"in {self.LLM_TYPE.keys()}."
            ) from exc

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

    def _init_state_graph(self):
        # Initialize the state graph
        setattr(
            self, 
            'state', 
            StateGraph(self.State)
        )
    
    def _init_tools(self, **kwargs):
        
        self.embedding = kwargs.get('embedding', '')
        self.vector_store = kwargs.get('vector_db', '')
        self.llm = kwargs.get('llm', '')
        self.generate_prompt_template = kwargs.get('generate_prompt', '')
        self.grader_prompt_template = kwargs.get('grader_prompt', '')
        self.query_rewrite_prompt_template = kwargs.get(
            'query_rewrite_prompt', ''
        )

        if self.llm is None:
            raise ValueError(
                "LLM must be initialized before tools."
            )
        
        if self.vector_store is None:
            raise ValueError(
                "Vector store must be initialized before tools."
            )

        structured_llm_grader = self.llm.with_structured_output(
            self.GradeDocuments
        )
        
        setattr(
            self, 
            'retriever', 
            self.vector_store.as_retriever()
        )

        setattr(
            self, 
            'wiki_searcher', 
            WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        )

        retrieval_grader = self.grader_prompt_template | structured_llm_grader
        
        setattr(
            self,
            'retrieval_grader_chain',
            retrieval_grader
        )

        generate = self.generate_prompt_template | self.llm | StrOutputParser()

        setattr(
            self,
            'generate_chain',
            generate
        )

        rewrite =\
            self.query_rewrite_prompt_template | self.llm | StrOutputParser()
        
        setattr(
            self,
            'question_rewriter_chain',
            rewrite
        )

    def init_workflow(self):
        pass

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
        documents = retriever.get_relevant_documents(question)
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
        generation = rag_chain.invoke({"context": documents, "question": question})
        return {
            "documents": documents, "question": question, "generation": generation
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
            score = self.retrieval_grader_chain.invoke(
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
        better_question = question_rewriter.invoke({"question": question})
        return {"documents": documents, "question": better_question}

    def human_approve(self, state) -> Command[Literal["human_input", "wiki_search"]]:
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
        documents = wikipedia.run(question)

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

    
