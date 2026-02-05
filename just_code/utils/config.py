"""Configuration management for Just Code."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def load_config() -> dict:
    """Load configuration from environment variables.

    Returns:
        Configuration dictionary with API keys, model settings, etc.
    """
    return {
        "api_key": os.getenv("ZHIPUAI_API_KEY"),
        "base_url": os.getenv("ZHIPUAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/"),
        "model": os.getenv("AGENT_MODEL", "glm-4-plus"),
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("AGENT_MAX_TOKENS", "4096")),
        "work_dir": os.getenv("WORK_DIR", os.getcwd()),
        "langchain_api_key": os.getenv("LANGCHAIN_API_KEY"),
        "langchain_tracing": os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true",
        "langchain_project": os.getenv("LANGCHAIN_PROJECT", "just-code"),
        "memory_max_entries": int(os.getenv("MEMORY_MAX_ENTRIES", "1000")),
        "memory_ttl_days": int(os.getenv("MEMORY_TTL_DAYS", "30")),
    }


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_state_dir() -> Path:
    """Get the directory for storing agent state and memory."""
    state_dir = get_project_root() / ".just_code_state"
    state_dir.mkdir(exist_ok=True)
    return state_dir
