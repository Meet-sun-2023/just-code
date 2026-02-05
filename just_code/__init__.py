"""Just Code - A terminal AI coding assistant powered by Deep Agents and GLM-4.7."""

__version__ = "0.1.0"

from just_code.models import get_llm, list_models
from just_code.agents import create_coding_agent, invoke_agent

__all__ = [
    "get_llm",
    "list_models",
    "create_coding_agent",
    "invoke_agent",
    "__version__",
]
