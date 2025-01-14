from email import message
import os
from typing import TypedDict
from openai import BadRequestError
import streamlit as st
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
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
#                   Parameters
# ========================================
if "enable_params_adjustment" not in st.session_state:
    st.session_state.enable_params_adjustment = False

if "log" not in st.session_state:
    st.session_state.log = None

if "history" not in st.session_state:
    st.session_state.history = []


@st.dialog("Enable for adjusting prompt and generate parameters")
def enable():
    st.warning("Are you sure to modify the parameters?")
    if st.button("Yes"):
        st.session_state.enable_params_adjustment = True
        st.rerun()


# ========================================
#                   System prompts
# ========================================
grader_default = """You are a grader assessing relevance of a retrieved document to a user question.
If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant.
Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

generate_default = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:"""

query_rewrite_default = """You a question re-writer that converts an input question to a better version that is optimized for retrival. Look at the input and try to reason about the underlying semantic intent / meaning."""

with st.sidebar:
    st.markdown("#### Prompts and Parameters")
    st.button(
        label="Enable adjustment",
        type="primary",
        on_click=enable,
    )
    disable = not st.session_state.enable_params_adjustment
    grader_system_prompt = st.text_area(
        label="Grader Prompt",
        value=grader_default,
        height=300,
        disabled=disable,
    )
    generate_system_prompt = st.text_area(
        label="Generate Prompt",
        value=generate_default,
        height=300,
        disabled=disable,
    )
    query_rewrite_system_prompt = st.text_area(
        label="Query Rewrite Prompt",
        value=query_rewrite_default,
        height=300,
        disabled=disable,
    )
    top_p = float(st.slider(
        label="Top-p",
        value=0.50,
        min_value=0.01,
        max_value=1.0,
        step=0.01,
        format="%.2f"  
    ))
    temperature = float(st.slider(
        label="Temperature",
        value=0.50,
        min_value=0.01,
        max_value=1.0,
        step=0.01,
        format="%.2f"
    ))
    max_token = int(st.slider(
        label="Max token",
        value=8000,
        min_value=10,
        max_value=8000
    ))


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
    openai_api_base=base_url, 
    openai_api_key=api_key, 
    model_name=model_name,
    temperature=temperature,
    top_p=top_p,
    max_tokens=max_token
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

retriever = vector_store.as_retriever()


# ========================================
#                   Grader
# ========================================
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", grader_system_prompt),
        (
            "human", 
            "Retrieved document: \n\n {document} \n\n User question: {question}"
        ),
    ]
)
retrieval_grader = grade_prompt | structured_llm_grader

# ========================================
#                   Generate
# ========================================
prompt = ChatPromptTemplate.from_template(generate_system_prompt)
rag_chain = prompt | llm | StrOutputParser()


# ========================================
#                 Query Re-write
# ========================================
re_write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", query_rewrite_system_prompt),
        (
            "human",
            "Here is the initial question: \n\n {question} \n Formulate an improved question.",
        ),
    ]
)
question_rewriter = re_write_prompt | llm | StrOutputParser()


# ========================================
#                   Graph state
# ========================================
class GraphState(TypedDict):
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
    transformed_question: str
    documents: list[str]
    rewrite_question: str
    rewrite_generation: str
    rewrite_documents: list[str]


# ========================================
#                   Nodes
# ========================================


def retrieve(state):
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


def extra_retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    question = state["rewrite_question"]

    # Retrieval
    documents = retriever.get_relevant_documents(question)
    return {"rewrite_documents": documents, "rewrite_question": question}


def generate(state):
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


def extra_generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    question = state["rewrite_question"]
    documents = state["rewrite_documents"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {
        "rewrite_documents": documents, 
        "rewrite_question": question, 
        "rewrite_generation": generation
    }


def grade_documents(state):
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
    transformed_question = "Yes"
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            transformed_question = "No"
            filtered_docs.append(d)
        else:
            continue
    return {
        "documents": filtered_docs, 
        "question": question, 
        "transformed_question": transformed_question
    }


def transform_query(state):
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
    return {"documents": documents, "rewrite_question": better_question}


# ========================================
#                   Edges
# ========================================
def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    transformed_question = state["transformed_question"]

    if transformed_question == "Yes":
        # All documents have been filtered check_relevance
        # We will re-generate a new query

        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        return "generate"


# ========================================
#                   Graph Init
# ========================================

# Compile application and test
workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generatae
workflow.add_node("transform_query", transform_query)  # transform_query
workflow.add_node("extra_retrieve", extra_retrieve)
workflow.add_node("extra_generate", extra_generate)

# Buikd Graph
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_edge("transform_query", "extra_retrieve")
workflow.add_edge("extra_retrieve", "extra_generate")
workflow.add_edge("extra_generate", END)

# Compile
app = workflow.compile()

# ========================================
#                   Streamlit
# ========================================


if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.history.append({"role": "user", "message": prompt})
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        inputs = {"question": prompt}
        try:
            response = [output for output in app.stream(inputs)]
            st.write(response[-1]["generate"]["generation"])
            st.session_state.history.append({"role": "assistant", "message": response[-1]["generate"]["generation"]})
            st.session_state.log = response
        except BadRequestError:
            st.error("Oops, it seems like the question is too complex or too long for me to answer. Please refresh the page abd try another question.")
            st.stop()

if st.session_state.log:
    if st.button("Show more"):
        for item in st.session_state.history:
            with st.chat_message(item["role"]):
                st.write(item["message"])
        st.write(st.session_state.log)        
