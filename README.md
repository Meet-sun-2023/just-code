# Just Code

A terminal AI coding assistant powered by LangChain Deep Agents and GLM-4.7.

## Features

Built on [LangChain Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview), Just Code comes with:

- **File Operations** - Read, write, edit files with context awareness
- **Code Search** - Search through your codebase with `glob` and `grep`
- **Shell Execution** - Run commands and scripts safely
- **Task Planning** - Built-in todo list for complex tasks
- **Subagents** - Delegate specialized work to dedicated agents
- **Persistent Memory** - Remember context across sessions

## Installation

```bash
# Clone the repository
cd /home/zczw/Projects/just_code

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Copy environment template and configure
cp .env.example .env
# Edit .env and add your ZHIPUAI_API_KEY
```

## Requirements

- Python 3.10+
- Zhipu AI API key ([Get one here](https://open.bigmodel.cn/))
- LangChain 1.0+
- deepagents

## Usage

```bash
# Check system status
just-code status

# List available GLM models
just-code models

# Test GLM connection
just-code test

# Start interactive chat
just-code chat

# Send a single prompt
just-code chat "Help me refactor this function"

# Use a specific model
just-code chat -m glm-4-flash "What's in this file?"
```

## Configuration

Create a `.env` file with your API keys:

```bash
# Required: Zhipu AI API key
ZHIPUAI_API_KEY=your_api_key_here

# Optional: Model selection (default: glm-4-plus)
AGENT_MODEL=glm-4-plus

# Optional: Temperature (default: 0.7)
AGENT_TEMPERATURE=0.7
```

## Available Models

### GLM-4.7 Series (Latest)
| Model | Description |
|-------|-------------|
| `glm-4.7` | Latest flagship model optimized for Agentic Coding |
| `glm-4.7-flashx` | Fast & lightweight for quick tasks |

### GLM-4 Series (Previous)
| Model | Description |
|-------|-------------|
| `glm-4-plus` | Most capable model for complex tasks |
| `glm-4-0520` | Balanced performance and cost |
| `glm-4-air` | Faster responses for simpler tasks |
| `glm-4-flash` | Fastest, ideal for quick interactions |

## Built-in Tools

Just Code includes these tools out of the box:

- **File System**: `ls`, `read_file`, `write_file`, `edit_file`
- **Search**: `glob`, `grep`
- **Shell**: `execute` (run commands)
- **Planning**: `write_todos` (manage task lists)
- **Subagents**: `task` (delegate to specialized agents)

## Project Structure

```
just_code/
├── just_code/           # Main package
│   ├── agents/          # Agent configurations
│   │   └── coding_agent.py
│   ├── models/          # LLM integrations (GLM-4.7)
│   │   └── glm.py
│   ├── utils/           # Helper utilities
│   │   ├── config.py
│   │   └── logger.py
│   └── cli.py           # CLI entry point
├── config/              # Configuration files
├── tests/               # Tests
└── docs/                # Documentation
```

## License

MIT
