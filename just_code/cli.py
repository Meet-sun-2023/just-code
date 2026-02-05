"""Just Code CLI - Main entry point."""

import re
import sys
import uuid
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint
from rich.syntax import Syntax
from rich.text import Text

from just_code.utils import get_logger, load_config
from just_code.models import get_llm, list_models
from just_code.agents import create_coding_agent, invoke_agent, stream_agent

console = Console()
logger = get_logger(__name__)

# Try importing prompt_toolkit for better input handling
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.styles import Style
    PROMPT_TOOLKIT_AVAILABLE = True
    # Define style for prompt
    PROMPT_STYLE = Style.from_dict({
        "prompt": "cyan bold",
    })
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

# Code block patterns for syntax highlighting
CODE_BLOCK_PATTERN = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)


@click.group()
@click.version_option(version="0.1.0", prog_name="just-code")
def cli() -> None:
    """Just Code - A terminal AI coding assistant powered by Deep Agents and GLM-4.7."""
    pass


@cli.command()
@click.argument("prompt", required=False)
@click.option("--model", "-m", help="Model to use (e.g., glm-4.7, glm-4.7-flashx)")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--stream", "-s", is_flag=True, help="Enable streaming output")
@click.option("--no-memory", is_flag=True, help="Disable conversation memory (stateless mode)")
def chat(prompt: str | None, model: str | None, debug: bool, stream: bool, no_memory: bool) -> None:
    """Start an interactive chat session or send a single prompt."""
    config = load_config()
    model_name = model or config.get("model", "glm-4.7")
    with_memory = not no_memory

    rprint(Panel(
        "[bold cyan]Just Code[/bold cyan]\n"
        "Powered by GLM-4.7 & LangChain Deep Agents\n\n"
        f"Model: [blue]{model_name}[/blue]"
        + (f" | [dim]Streaming: ON[/dim]" if stream else "")
        + (f" | [dim]Memory: {'OFF' if no_memory else 'ON'}[/dim]"),
        title_align="center",
    ))

    try:
        # Create agent
        rprint("[dim]Initializing agent...[/dim]")
        agent = create_coding_agent(model=model_name, debug=debug, with_memory=with_memory)

        if prompt:
            # Single prompt mode (stateless, no thread_id)
            if stream:
                _process_message_stream(agent, prompt)
            else:
                _process_message(agent, prompt)
        else:
            # Interactive mode (with memory by default)
            _interactive_loop(agent, stream)

    except ImportError as e:
        rprint(f"\n[bold red]Error:[/bold red] {e}")
        rprint("\n[yellow]Install deepagents:[/yellow]")
        rprint("  pip install deepagents")
    except Exception as e:
        rprint(f"\n[bold red]Error:[/bold red] {e}")
        logger.exception("Chat error")


def _process_message(agent, message: str, thread_id: str | None = None) -> None:
    """Process a single message through the agent (non-streaming)."""
    rprint(f"\n[yellow]You:[/yellow] {message}")

    with console.status("[bold green]Thinking...", spinner="dots"):
        result = invoke_agent(agent, message, thread_id=thread_id)

    # Display response
    _display_result(result)


def _process_message_stream(agent, message: str, thread_id: str | None = None) -> None:
    """Process a single message with streaming output."""
    rprint(f"\n[yellow]You:[/yellow] {message}")

    rprint("\n[bold green]just-code:[/bold green] ", end="")
    full_response = ""
    response_started = False

    for chunk in stream_agent(agent, message):
        # Stream returns dict with various keys from middleware
        # Deep Agents can return chunks with different structures
        for key, value in chunk.items():
            if value is None:
                continue

            # Handle messages in different formats
            messages = None
            if isinstance(value, dict) and "messages" in value:
                messages = value["messages"]
            elif isinstance(value, list):
                messages = value
            # Handle Overwrite object from Deep Agents
            elif hasattr(value, "value"):
                messages = value.value

            if messages:
                # Ensure messages is a list
                if not isinstance(messages, list):
                    continue

                for msg in messages:
                    content = None

                    # Extract content from different message types
                    if hasattr(msg, "type"):
                        if msg.type == "ai":
                            content = getattr(msg, "content", None)
                    elif isinstance(msg, dict):
                        if msg.get("role") == "assistant" or msg.get("type") == "ai":
                            content = msg.get("content")

                    # Stream the content
                    if content:
                        if isinstance(content, str) and content:
                            if not response_started:
                                response_started = True
                            # Print new content only (incremental)
                            new_content = content[len(full_response):]
                            if new_content:
                                full_response = content
                                # Use stdout.write for better streaming
                                import sys
                                sys.stdout.write(new_content)
                                sys.stdout.flush()

    rprint()  # New line after streaming

    # Show formatted response only if it contains code blocks
    # (to avoid duplicate output for plain text responses)
    if full_response and CODE_BLOCK_PATTERN.search(full_response):
        rprint("\n[dim]--- Formatted Code Blocks ---[/dim]")
        _print_assistant_message(full_response)


def _display_result(result: dict) -> None:
    """Display agent result to the user with syntax highlighting."""
    messages = result.get("messages", [])

    for msg in messages:
        # Handle both dict and Message object
        if hasattr(msg, "type"):
            # Message object (HumanMessage, AIMessage, etc.)
            if msg.type == "ai":
                content = msg.content if hasattr(msg, "content") else str(msg)
                _print_assistant_message(content)
        elif isinstance(msg, dict):
            # Dict format
            if msg.get("role") == "assistant" or msg.get("type") == "ai":
                content = msg.get("content", "")
                _print_assistant_message(content)

    rprint()


def _print_assistant_message(content: str) -> None:
    """Print assistant message with markdown and code syntax highlighting."""
    # Check for code blocks and apply syntax highlighting
    parts = []
    last_end = 0

    for match in CODE_BLOCK_PATTERN.finditer(content):
        # Add text before code block as markdown
        if match.start() > last_end:
            text_part = content[last_end:match.start()]
            if text_part.strip():
                try:
                    md = Markdown(text_part)
                    rprint("\n[bold green]just-code:[/bold green]")
                    rprint(md)
                except:
                    rprint(f"\n[bold green]just-code:[/bold green] {text_part}")

        # Add code block with syntax highlighting
        lang = match.group(1) or "text"
        code = match.group(2)
        parts.append((lang, code))
        last_end = match.end()

    # Add remaining text
    if last_end < len(content):
        text_part = content[last_end:]
        if text_part.strip():
            try:
                md = Markdown(text_part)
                rprint("\n[bold green]just-code:[/bold green]")
                rprint(md)
            except:
                rprint(f"\n[bold green]just-code:[/bold green] {text_part}")

    # Display code blocks with syntax highlighting
    for lang, code in parts:
        try:
            syntax = Syntax(code, lang, theme="monokai", line_numbers=True)
            rprint("\n[bold green]just-code:[/bold green]")
            rprint(syntax)
        except:
            # Fallback if language is not supported
            rprint(f"\n[bold green]just-code:[/bold green] ```{lang}")
            rprint(code)
            rprint("```")


def _interactive_loop(agent, stream: bool = False) -> None:
    """Run interactive chat loop."""
    rprint("\n[green]Interactive mode started. Press Ctrl+C to exit.[/green]")
    rprint("[dim]Conversation memory is enabled. Context is preserved across messages.[/dim]")
    if stream:
        rprint("[dim]Streaming is enabled. Use /stream to toggle.[/dim]")
    rprint("[dim]Commands: /exit, /quit, /stream, /clear, /status[/dim]\n")

    message_count = 0
    # Generate a unique thread ID for this conversation session
    thread_id = str(uuid.uuid4())

    # Use prompt_toolkit for better Unicode handling if available
    if PROMPT_TOOLKIT_AVAILABLE:
        session = PromptSession()

    while True:
        try:
            # Use prompt_toolkit for better input handling (Chinese characters, etc.)
            if PROMPT_TOOLKIT_AVAILABLE:
                user_input = session.prompt(
                    [("class:prompt", "You: ")],
                    style=PROMPT_STYLE,
                    enable_suspend=True
                ).strip()
            else:
                # Fallback to standard input()
                try:
                    user_input = input("\033[36m\033[1mYou:\033[0m ").strip()
                except (EOFError, KeyboardInterrupt):
                    rprint()
                    break

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ("/exit", "/quit", "q"):
                rprint("\n[yellow]Goodbye![/yellow]")
                break
            elif user_input.lower() == "/stream":
                stream = not stream
                status = "ON" if stream else "OFF"
                rprint(f"\n[yellow]Streaming toggled: {status}[/yellow]")
                continue
            elif user_input.lower() == "/clear":
                # Reset thread ID to start a fresh conversation
                thread_id = str(uuid.uuid4())
                message_count = 0
                rprint("\n[yellow]Conversation cleared. Starting fresh session.[/yellow]")
                continue
            elif user_input.lower() == "/status":
                rprint(f"\n[dim]Session ID: {thread_id}[/dim]")
                rprint(f"[dim]Messages: {message_count}[/dim]")
                rprint(f"[dim]Streaming: {'ON' if stream else 'OFF'}[/dim]")
                continue

            # Show message echo
            message_count += 1
            rprint(f"\n[yellow]Message #{message_count}:[/yellow] {user_input}")

            # Process message with thread_id for memory continuity
            if stream:
                _process_message_stream(agent, user_input, thread_id=thread_id)
            else:
                _process_message(agent, user_input, thread_id=thread_id)

        except KeyboardInterrupt:
            rprint("\n\n[yellow]Use /exit or /quit to exit properly.[/yellow]")
        except EOFError:
            rprint("\n\n[yellow]Goodbye![/yellow]")
            break


@cli.command()
@click.option("--model", "-m", help="Model to use (e.g., glm-4.7, glm-4.7-flashx)")
def test(model: str | None) -> None:
    """Test GLM model connection."""
    try:
        rprint("\n[bold cyan]Testing GLM Connection[/bold cyan]\n")

        # Get available models
        models = list_models()
        rprint("[dim]Available models:[/dim]")
        for name, desc in models.items():
            rprint(f"  [blue]{name}[/blue]: {desc}")
        rprint()

        # Initialize model
        rprint(f"[dim]Initializing model: {model or 'glm-4.7'}[/dim]")
        llm = get_llm(model=model)

        # Test invocation
        rprint("[dim]Sending test prompt...[/dim]")
        from langchain_core.messages import HumanMessage

        response = llm.invoke([HumanMessage(content="Say 'Hello, GLM is working!' in JSON format.")])

        rprint("\n[bold green]Success![/bold green]")
        rprint(f"[dim]Response:[/dim] {response.content}")
        rprint()

    except Exception as e:
        rprint(f"\n[bold red]Error:[/bold red] {e}")
        raise click.ClickException(f"GLM test failed: {e}")


@cli.command()
def models() -> None:
    """List available GLM models."""
    models = list_models()

    console.print("\n[bold cyan]Available GLM Models[/bold cyan]\n")
    for name, desc in models.items():
        console.print(f"  [blue]{name}[/blue]: {desc}")
    console.print()


@cli.command()
def status() -> None:
    """Show system status and configuration."""
    config = load_config()

    console.print("\n[bold cyan]Just Code Status[/bold cyan]\n")

    # API Configuration
    api_status = "[green]Connected[/green]" if config.get("api_key") else "[red]Not configured[/red]"
    console.print(f"  API: {api_status}")
    console.print(f"  Model: {config.get('model', 'glm-4.7')}")
    console.print(f"  Temperature: {config.get('temperature', 0.7)}")

    # Deep Agents
    try:
        from deepagents import create_deep_agent
        console.print(f"  Deep Agents: [green]Installed[/green]")
    except ImportError:
        console.print(f"  Deep Agents: [red]Not installed[/red]")

    # Working Directory
    import os
    console.print(f"  Working Dir: {os.getcwd()}")

    console.print()


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
