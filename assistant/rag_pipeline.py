"""RAG pipeline placeholder for policy-grounded explanations."""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

from __future__ import annotations


def retrieve_policy_context(_: dict) -> str:
    return "AML policy retrieval not implemented yet."
