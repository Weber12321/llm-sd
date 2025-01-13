import os
from typing import List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_community.vectorstores import OpenSearchVectorSearch
import streamlit as st
from utils.client.embedding import EmbeddingClient
from langgraph.graph import START, StateGraph

from langchain_core.prompts import PromptTemplate

st.title("Simple RAG")


# setup environment variable
base_url = os.getenv("VLLM_HOST", "")
api_key = os.getenv("VLLM_API_KEY", "")
vector_db_host = os.getenv("VECTORDB_HOST", "")
embedding_host = os.getenv("EMBEDDING_HOST", "")
vector_db_index = os.getenv("VECTORDB_INDEX", "")
model_name = os.getenv("MODEL_NAME", "")


llm = ChatOpenAI(
    openai_api_base=base_url, openai_api_key=api_key, model_name=model_name
)

embedding_client = EmbeddingClient(
    embedding_api_path=embedding_host,
    request_timeout=600
)

vector_store = OpenSearchVectorSearch(
    index_name=vector_db_index,
    embedding_function=embedding_client,
    opensearch_url=vector_db_host,
)

template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
Always say "thanks for asking!" at the end of the answer.

{context}

Question: {question}

Helpful Answer:"""
prompt_template = PromptTemplate.from_template(template)


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt_template.invoke({"question": state["question"], "context": docs_content})
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
