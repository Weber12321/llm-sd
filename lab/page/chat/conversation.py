import os
import logging
from openai import OpenAI

import streamlit as st

st.title("Simple chat")


base_url = os.getenv("VLLM_HOST", "http://localhost:8000/v1")
api_key = os.getenv("VLLM_API_KEY", "")

logging.info(base_url)
logging.info(api_key)


client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)


# Model param
with st.sidebar:
    st.markdown("#### 選擇模型參數")
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
        value=2000,
        min_value=10,
        max_value=8000
    ))

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add system prompt and greeting
if not st.session_state.messages:
    system_prompt = "你是一位專業的企業助理，回答任何使用者的問題。"
    greeting = "早安，請問您需要什麼協助?"
    st.session_state.messages.append({
        "role": "system", "content": system_prompt + "\n\n" + greeting})

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = os.getenv("MODEL_NAME", "")

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