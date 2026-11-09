# Terminant

**An AI-powered terminal agent, built from scratch in Python.**

Terminant brings an AI agent directly into the terminal, combining LLM-powered reasoning, native tool execution, and a real-time terminal UI.

## Features

- **Interactive TUI** — Chat with the agent through a Textual terminal interface.
- **Agent loop** — A custom agent loop that handles LLM responses, tool calls, and tool results.
- **Native tool execution** — Execute registered tools through the agent, including terminal, filesystem, and Git operations.
- **Event-driven architecture** — An event bus connects internal activity with the UI.
- **Activity monitoring** — A dedicated panel displays tool calls and internal runtime activity.
- **OpenRouter support** — Connect to LLMs through the OpenRouter API.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Textual | Terminal user interface |
| Rich | Terminal rendering |
| OpenAI SDK | LLM API integration |
| OpenRouter | Model provider |
| GitPython | Git operations |
| Pytest | Testing |

## Getting Started

### Prerequisites

- Python 3.11+
- An [OpenRouter API key](https://openrouter.ai/)

### Installation

Clone the repository:

```bash
git clone https://github.com/0xEvsky/Terminant.git
cd Terminant
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
```

Install the project and its development dependencies:

```bash
pip install -e ".[dev]"
```

### Configuration

Set your OpenRouter API key:

**Linux / macOS**

```bash
export OPENROUTER_API_KEY="your-api-key"
```

**Windows (PowerShell)**

```powershell
$env:OPENROUTER_API_KEY="your-api-key"
```

### Run

```bash
python main.py
```

## Architecture

Terminant is built around a custom agent loop rather than relying on an agent orchestration framework.

At a high level, the interaction follows this flow:

```text
           User Input
                |
                v
          Agent Loop
                |
                v
          LLM Provider
                |
         +------+------+
         |             |
     Text Reply     Tool Calls
                       |
                       v
                 Tool Registry
                       |
                       v
                 Tool Execution
                       |
                       v
                  Tool Results
                       |
                       v
                   Agent Loop
```

An event bus communicates runtime activity to the UI, allowing the application to display tool calls and internal events as they happen.

## Project Structure

```text
Terminant/
├── agent/       # Agent loop and conversation memory
├── config/      # Application configuration
├── events/      # Event definitions and event bus
├── llm/         # LLM client, response parsing, and prompts
├── tools/       # Agent tools: filesystem, terminal, Git, etc.
├── ui/          # Textual application, widgets, and styling
├── tests/       # Automated tests
├── main.py      # Application entry point
├── logger.py    # Logging utilities
└── pyproject.toml
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov
```

---