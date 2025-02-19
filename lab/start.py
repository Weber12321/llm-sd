import logging
import sys
import streamlit as st


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    stream=sys.stdout)


pages = {
    "Prompt": [
        # st.Page(
        #     "page/prompts/prompt_lab.py",
        #     title="Prompt 實驗室"
        # ),
        # st.Page(
        #     "page/prompts/ask_prompt.py",
        #     title="猜你想問實驗室"
        # )
    ],
    "Chat": [
        st.Page(
            "page/chat/conversation.py",
            title="simple chat"
        ),
        st.Page(
            "page/chat/rag_conversation.py",
            title="simple RAG"
        ),
        st.Page(
            "page/chat/crag.py",
            title="Corrective RAG"
        )
    ]
}


pg = st.navigation(pages)
pg.run()