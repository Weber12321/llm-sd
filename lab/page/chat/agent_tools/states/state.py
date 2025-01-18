from typing import TypedDict


class RetrivalState(TypedDict):
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