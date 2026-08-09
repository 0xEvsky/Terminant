# Terminant

Terminant is a small AI terminal assistant with a Textual TUI, live chat, and a side log panel for tool calls and internal activity.

## What it does

- Chat with an LLM from the terminal UI
- Execute registered tools through the agent loop
- Show runtime logs and event activity in a side panel

## Run

Set `OPENROUTER_API_KEY`, then start the app with:

```bash
python main.py
```

## Notes

- The UI is built with Textual.
- The default model is configured in `config/config.py`.
