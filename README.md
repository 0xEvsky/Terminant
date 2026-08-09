# Terminant

Terminant is a small AI terminal assistant with a Textual TUI, live chat, and a side log panel for tool calls and internal activity.

## What it does?

- Chat with an LLM from the terminal UI
- Execute registered tools through the agent loop
- Show runtime logs and event activity in a side panel

## Project structure

- `main.py`: app entrypoint
- `agent/`: agent loop and memory
- `llm/`: model client, parser, and prompts
- `tools/`: filesystem and terminal tools
- `ui/`: Textual app, widgets, and styling
- `events/`: event definitions and bus
- `config/`: API key and model defaults

## Run

Set `OPENROUTER_API_KEY`, then start the app with:

```bash
python main.py
```
