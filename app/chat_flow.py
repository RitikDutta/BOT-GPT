import os
from typing import Dict
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from .config import GENAI_MODEL, GOOGLE_API_KEY
from .database.relational import add_message

# set API key for Google GenAI client (auto set by env var, but just to be sure [not to be dont on production])
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

llm = init_chat_model(
    f"google_genai:{GENAI_MODEL}",
    temperature=0.3,
)

# prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are BOT-GPT, a helpful assistant. be consise and friendly"
        ),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ]
)

# LCEL chain (new way to bind in langchain)
base_chain = prompt | llm

# in-memory session store
_session_store: Dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _session_store:
        _session_store[session_id] = InMemoryChatMessageHistory()
    return _session_store[session_id]

chain_with_history = RunnableWithMessageHistory(
    base_chain, 
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

def ask_bot(session_id: str, user_input: str):
    """ handles the chat endpoint with db"""
    add_message(session_id=session_id, role="user", content=user_input)

    config = {"configurable": {"session_id": session_id}}
    response = chain_with_history.invoke({"input": user_input}, config=config)
    reply_text = response.content
    add_message(session_id=session_id, role="assistant", content=reply_text)

    return reply_text
