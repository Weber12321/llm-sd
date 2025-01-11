import os
from typing import List, TypedDict
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_community.vectorstores import OpenSearchVectorSearch
import streamlit as st
from utils.client.embedding import EmbeddingClient
from langgraph.graph import START, StateGraph

st.title("Simple chat")


# setup environment variable
base_url = os.getenv("VLLM_HOST", "")
api_key = os.getenv("VLLM_API_KEY", "")
vector_db_host = os.getenv("VECTORDB_HOST", "")
embedding_host = os.getenv("EMBEDDING_HOST", "")
vector_db_index = os.getenv("VECTORDB_INDEX", "")
model_name = os.getenv("MODEL_NAME", "")

# client = OpenAI(
#     base_url=base_url,
#     api_key=api_key,
# )
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
    opensearch_url=embedding_client,
)

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
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "system":
        with st.chat_message("assistant"):
            st.markdown(message["content"].split("\n\n")[1])
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            max_tokens=max_token,
            temperature=temperature,
            top_p=top_p,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({
        "role": "assistant", "content": response})