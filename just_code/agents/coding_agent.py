"""Coding agent implementation using LangChain Deep Agents."""

import os
import uuid
from pathlib import Path
from typing import Iterator

from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver

from just_code.models import get_llm
from just_code.utils import get_logger, load_config
from just_code.tools import git_tools

logger = get_logger(__name__)

# Try importing deepagents
try:
    from deepagents import create_deep_agent
    from deepagents.backends import FilesystemBackend
    DEEPAGENTS_AVAILABLE = True
except ImportError:
    DEEPAGENTS_AVAILABLE = False
    logger.warning("deepagents not installed. Please run: pip install deepagents")


# Global in-memory checkpointer for conversation history
# In production, consider using a persistent checkpointer like PostgresSaver
_checkpointer = MemorySaver()


def create_coding_agent(
    model: str | None = None,
    system_prompt: str | None = None,
    debug: bool = False,
    with_memory: bool = True,
) -> CompiledStateGraph:
    """Create a coding agent using Deep Agents.

    The agent comes with built-in tools for:
    - File operations: read, write, edit files
    - Code search: glob, grep
    - Shell execution: run commands
    - Planning: todo list management
    - Subagents: delegate specialized tasks

    Args:
        model: GLM model name (e.g., "glm-4.7", "glm-4.7-flashx")
        system_prompt: Optional custom system prompt
        debug: Enable debug mode
        with_memory: Enable conversation memory using checkpointer

    Returns:
        Compiled deep agent ready for invocation

    Raises:
        ImportError: If deepagents is not installed
    """
    if not DEEPAGENTS_AVAILABLE:
        raise ImportError(
            "deepagents is not installed. "
            "Install it with: pip install deepagents"
        )

    # Get GLM model
    llm = get_llm(model=model)
    logger.info(f"Creating coding agent with model: {model or 'glm-4.7'}")

    # Default system prompt for coding assistant
    if system_prompt is None:
        system_prompt = """You are Just Code, an AI coding assistant.

You help users with:
- Writing and editing code
- Debugging and fixing errors
- Explaining code and concepts
- Refactoring and optimizing
- Running tests and commands

Best practices:
1. Read files before editing them
2. Use grep/glob to find code
3. Run commands to test changes
4. Explain your reasoning clearly
5. Ask for clarification when needed
6. Remember context from previous messages in the conversation
"""

    # Get working directory from config or use current directory
    config = load_config()
    work_dir = config.get("work_dir", os.getcwd())

    # Create deep agent with FilesystemBackend for real file access
    # Add custom git tools to the built-in tools
    agent = create_deep_agent(
        model=llm,
        system_prompt=system_prompt,
        backend=lambda rt: FilesystemBackend(root_dir=work_dir, virtual_mode=True),
        tools=git_tools,
        checkpointer=_checkpointer if with_memory else None,
        debug=debug,
    )

    return agent


def invoke_agent(
    agent: CompiledStateGraph,
    message: str,
    thread_id: str | None = None,
    files: dict[str, str] | None = None,
) -> dict:
    """Invoke the coding agent with a message (non-streaming).

    Args:
        agent: The compiled agent from create_coding_agent
        message: User message/input
        thread_id: Conversation thread ID for memory continuity.
                   If None, generates a new thread ID for each call.
        files: Optional files to provide context (path -> content mapping)

    Returns:
        Agent response with messages and intermediate steps
    """
    # Generate thread_id if not provided (for stateless conversations)
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    agent_config = {
        "recursion_limit": 1000,
        "configurable": {"thread_id": thread_id},
    }

    # Prepare input
    inputs = {
        "messages": [{"role": "user", "content": message}],
    }

    # Add files if provided
    if files:
        inputs["files"] = files

    # Invoke agent
    result = agent.invoke(inputs, config=agent_config)

    return result


def stream_agent(
    agent: CompiledStateGraph,
    message: str,
    thread_id: str | None = None,
    files: dict[str, str] | None = None,
) -> Iterator[dict]:
    """Stream the coding agent response.

    Args:
        agent: The compiled agent from create_coding_agent
        message: User message/input
        thread_id: Conversation thread ID for memory continuity.
                   If None, generates a new thread ID for each call.
        files: Optional files to provide context (path -> content mapping)

    Yields:
        Streaming chunks from the agent (messages and updates)
    """
    # Generate thread_id if not provided (for stateless conversations)
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    agent_config = {
        "recursion_limit": 1000,
        "configurable": {"thread_id": thread_id},
    }

    # Prepare input
    inputs = {
        "messages": [{"role": "user", "content": message}],
    }

    # Add files if provided
    if files:
        inputs["files"] = files

    # Stream agent response using LangChain 1.0's built-in stream method
    for chunk in agent.stream(inputs, config=agent_config):
        yield chunk
