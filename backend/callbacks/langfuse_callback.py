"""
Langfuse Callback Handler Module
"""
import os
from langfuse.langchain import CallbackHandler
from dotenv import load_dotenv

load_dotenv()

def get_langfuse_manager(
    session_id: str,
    user_email: str | None = None,
):
    """
    Returns a LangChain callback configuration for Langfuse.
    """
    handler = CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
        session_id=session_id,
        user_id=user_email,
        trace_name="travel_planner_chat",
        tags=["fastapi", "langchain", "observability"],
    )

    return {"callbacks": [handler]}
