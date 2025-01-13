import os
from typing import List, TypedDict

import streamlit as st
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from utils.client.embedding import EmbeddingClient

st.title("Corrective RAG")


# setup environment variable
base_url = os.getenv("VLLM_HOST", "")
api_key = os.getenv("VLLM_API_KEY", "")
vector_db_host = os.getenv("VECTORDB_HOST", "")
embedding_host = os.getenv("EMBEDDING_HOST", "")
vector_db_index = os.getenv("VECTORDB_INDEX", "")
model_name = os.getenv("MODEL_NAME", "")


# ========================================
#                   Data Model
# ========================================
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


# ========================================
#                   Clients
# ========================================
llm = ChatOpenAI(
    openai_api_base=base_url, openai_api_key=api_key, model_name=model_name
)
structured_llm_grader = llm.with_structured_output(GradeDocuments)
embedding_client = EmbeddingClient(
    embedding_api_path=embedding_host,
    request_timeout=600
)
vector_store = OpenSearchVectorSearch(
    index_name=vector_db_index,
    embedding_function=embedding_client,
    opensearch_url=vector_db_host,
)

# ========================================
#                   Grader
# ========================================
# Prompt
system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader

# ========================================
#                   Generate
# ========================================


# Prompt
template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:"""
prompt = ChatPromptTemplate.from_template(template)

# LLM
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Chain
rag_chain = prompt | llm | StrOutputParser()


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    web_search = "No"
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            web_search = "Yes"
            continue
    return {"documents": filtered_docs, "question": question, "web_search": web_search}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt_template.invoke({
        "question": state["question"], "context": docs_content
    })
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):

        st.write_stream(
            graph.stream({"question": prompt}, stream_mode="updates")
        )
        # for message, metadata in graph.stream(
        #     {"question": prompt}, stream_mode="messages"
        # ):
        #     response = st.write(message.content)
