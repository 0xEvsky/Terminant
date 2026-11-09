"""Textual-based TUI application for Terminant."""

import sys
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Header,
    Footer,
    Static,
    Input,
    RichLog,
    Label,
    TabbedContent,
    TabPane,
)
from textual.reactive import reactive
from textual.message import Message
from textual.events import Key

from events.event_bus import EventBus
from events.agent_events import (
    UserMessageSubmitted,
    AssistantMessageFinished,
    StreamingToken,
    ConversationLoaded,
    AgentIdle,
    AgentBusy,
    ToolStarted,
    ToolCallSucceeded,
    ToolCallFailed,
    APICallFailed,
    ErrorEvent,
    ThinkingStarted,
)
from ui.widgets.logs_view import LogsView
from ui.widgets.base import AgentWidget
from logger import log_info, log_error


class ChatMessage(Message):
    """Message for chat messages."""

    def __init__(self, content: str, is_user: bool = False, is_system: bool = False) -> None:
        self.content = content
        self.is_user = is_user
        self.is_system = is_system
        super().__init__()


class StatusUpdate(Message):
    """Message for status updates."""

    def __init__(self, status: str, is_busy: bool = False) -> None:
        self.status = status
        self.is_busy = is_busy
        super().__init__()


class ToolStatus(Message):
    """Message for tool execution status."""

    def __init__(self, tool_name: str, status: str, details: str = "") -> None:
        self.tool_name = tool_name
        self.status = status  # "started", "finished", "failed"
        self.details = details
        super().__init__()


class TerminantApp(App):
    """Textual-based TUI application for Terminant."""

    CSS = """
    TerminantApp {
        background: $surface;
    }

    #main-container {
        layout: vertical;
        height: 100%;
    }

    #content-area {
        height: 1fr;
        layout: horizontal;
    }

    #left-pane {
        width: 1fr;
        height: 100%;
        align: center middle;
    }

    #chat-input-group {
        width: 100%;
        height: auto;
        max-height: 100%;
        layout: vertical;
    }

    #chat-area {
        width: 100%;
        height: auto;
        max-height: 90%;
        min-height: 8;
        overflow-y: hidden;
        padding: 1;
        border: solid $primary;
        margin: 1;
        background: $surface;
    }

    #chat-log {
        height: auto;
        max-height: 100%;
        overflow-y: auto;
    }

    #input-area {
        width: 100%;
        height: 3;
        padding: 0 1;
        margin: 1;
        layout: horizontal;
    }

    #input-field {
        width: 1fr;
        height: 100%;
        margin-right: 1;
        border: solid $primary;
    }

    #input-field:focus {
        border: solid $accent;
    }

    #send-button {
        width: 10;
    }

    #logs-panel {
        width: 40;
        height: 100%;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }

    #logs-title {
        text-style: bold;
        margin-bottom: 1;
    }

    #status-bar {
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #tabs {
        height: 100%;
    }

    .user-message {
        color: $success;
        text-style: bold;
    }

    .assistant-message {
        color: $text;
    }

    .system-message {
        color: $warning;
        text-style: italic;
    }

    .tool-message {
        color: $accent;
    }

    .error-message {
        color: $error;
        text-style: bold;
    }

    #input-field:focus {
        border: solid $accent;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+d", "quit", "Quit"),
        ("escape", "clear_input", "Clear Input"),
    ]

    status_text = reactive("Ready")
    is_busy = reactive(False)

    def __init__(self, event_bus: EventBus, **kwargs):
        super().__init__(**kwargs)
        self.event_bus = event_bus
        self.chat_log: Optional[RichLog] = None
        self.input_field: Optional[Input] = None
        self.status_label: Optional[Static] = None
        self.logs_view: Optional[LogsView] = None
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        """Set up event subscriptions for the UI."""
        self.event_bus.subscribe(AssistantMessageFinished, self._on_assistant_message)
        self.event_bus.subscribe(StreamingToken, self._on_streaming_token)
        self.event_bus.subscribe(AgentIdle, self._on_agent_idle)
        self.event_bus.subscribe(AgentBusy, self._on_agent_busy)
        self.event_bus.subscribe(ConversationLoaded, self._on_conversation_loaded)
        self.event_bus.subscribe(ToolStarted, self._on_tool_started)
        self.event_bus.subscribe(ToolCallSucceeded, self._on_tool_succeeded)
        self.event_bus.subscribe(ToolCallFailed, self._on_tool_failed)
        self.event_bus.subscribe(APICallFailed, self._on_api_failed)
        self.event_bus.subscribe(ErrorEvent, self._on_error)
        self.event_bus.subscribe(ThinkingStarted, self._on_thinking_started)

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header(show_clock=True)

        with Container(id="main-container"):
            # Content area (chat + input on left, logs on right)
            with Horizontal(id="content-area"):
                # Left pane: contains the centered chat+input group
                with Vertical(id="left-pane"):
                    # Chat + input as a single centered group
                    with Vertical(id="chat-input-group"):
                        # Chat area
                        with Vertical(id="chat-area"):
                            self.chat_log = RichLog(
                                id="chat-log",
                                markup=True,
                                highlight=False,
                                wrap=True,
                                auto_scroll=True,
                            )
                            yield self.chat_log

                        # Input area (immediately below chat area)
                        with Horizontal(id="input-area"):
                            self.input_field = Input(
                                placeholder="Type your message... (Enter to send, Ctrl+D to quit)",
                                id="input-field",
                            )
                            yield self.input_field

                # Logs panel (side panel, independent)
                with Vertical(id="logs-panel"):
                    yield Label("Logs", id="logs-title")
                    self.logs_view = LogsView(event_bus=self.event_bus, id="logs-view")
                    yield self.logs_view

            # Status bar
            self.status_label = Static("Ready", id="status-bar")
            yield self.status_label

            yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.title = "Terminant"
        self.sub_title = "AI Assistant"

        # Focus the input field
        if self.input_field:
            self.input_field.focus()

        # Print welcome message
        self._add_system_message("Terminant - Type your message and press Enter to send.")
        self._add_system_message("Type '/exit' or press Ctrl+D to quit.")

    def _add_system_message(self, message: str) -> None:
        """Add a system message to the chat log."""
        if self.chat_log:
            self.chat_log.write(f"[dim italic]{message}[/]")

    def _add_user_message(self, message: str) -> None:
        """Add a user message to the chat log."""
        if self.chat_log:
            self.chat_log.write(f"[bold green]►[/bold green] {message}")

    def _add_assistant_message(self, message: str) -> None:
        """Add an assistant message to the chat log."""
        if self.chat_log:
            self.chat_log.write(f"[bold blue]▸[/bold blue] {message}")

    def _add_tool_message(self, message: str) -> None:
        """Add a tool-related message to the chat log."""
        if self.chat_log:
            self.chat_log.write(f"[yellow]{message}[/yellow]")

    def _add_error_message(self, message: str) -> None:
        """Add an error message to the chat log."""
        if self.chat_log:
            self.chat_log.write(f"[bold red]✗ {message}[/bold red]")

    def _filter_model_formatting(self, text: str) -> str:
        """Filter out model formatting markers."""
        import re
        if not isinstance(text, str):
            return text

        # Remove bold formatting: **text** or __text__
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'__(.*?)__', r'\1', text)

        # Remove italic formatting: *text* or _text_
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'_(.*?)_', r'\1', text)

        # Remove inline code formatting: `text`
        text = re.sub(r'`(.*?)`', r'\1', text)

        # Remove ''text'' formatting
        text = re.sub(r"''(.*?)''", r'\1', text)

        return text

    # Event handlers for agent events

    def _on_assistant_message(self, event: AssistantMessageFinished) -> None:
        """Handle assistant message finished event."""
        filtered_message = self._filter_model_formatting(event.message)
        self.call_from_thread(self._add_assistant_message, filtered_message)

    def _on_streaming_token(self, event: StreamingToken) -> None:
        """Handle streaming token event."""
        # For now, we'll buffer and show complete messages
        # Could be enhanced to show streaming
        pass

    def _on_agent_idle(self, event: AgentIdle) -> None:
        """Handle agent idle event."""
        self.call_from_thread(self._set_status, "Ready", False)
        if self.input_field and not self.input_field.has_focus:
            self.call_from_thread(self.input_field.focus)

    def _on_agent_busy(self, event: AgentBusy) -> None:
        """Handle agent busy event."""
        self.call_from_thread(self._set_status, "Processing...", True)

    def _on_conversation_loaded(self, event: ConversationLoaded) -> None:
        """Handle conversation loaded event."""
        if self.chat_log:
            self.call_from_thread(self.chat_log.clear)
            self.call_from_thread(self._add_system_message, "Conversation loaded.")

    def _on_tool_started(self, event: ToolStarted) -> None:
        """Handle tool started event."""
        tool_name = event.tool_name
        self.call_from_thread(self._add_tool_message, f"🔧 Tool started: {tool_name}")

    def _on_tool_succeeded(self, event: ToolCallSucceeded) -> None:
        """Handle tool succeeded event."""
        tool_name = event.tool_name
        self.call_from_thread(self._add_tool_message, f"✓ Tool succeeded: {tool_name}")

    def _on_tool_failed(self, event: ToolCallFailed) -> None:
        """Handle tool failed event."""
        self.call_from_thread(self._add_error_message, f"Tool '{event.tool_name}' failed: {event.error}")

    def _on_api_failed(self, event: APICallFailed) -> None:
        """Handle API call failed event."""
        self.call_from_thread(self._add_error_message, f"API call failed: {event.error}")

    def _on_error(self, event: ErrorEvent) -> None:
        """Handle generic error event."""
        self.call_from_thread(self._add_error_message, f"Error: {event.error}")

    def _on_thinking_started(self, event: ThinkingStarted) -> None:
        """Handle thinking started event."""
        self.call_from_thread(self._set_status, "Thinking...", True)

    def _set_status(self, status: str, busy: bool) -> None:
        """Update the status bar."""
        self.status_text = status
        self.is_busy = busy
        if self.status_label:
            prefix = "⏳ " if busy else "✓ "
            self.status_label.update(f"{prefix}{status}")

    # Input handling

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "input-field":
            user_input = event.value.strip()
            if not user_input:
                return

            # Check for exit command
            if user_input == "/exit":
                self.exit()
                return

            # Add user message to chat
            self._add_user_message(user_input)

            # Clear input using Textual's method
            event.input.clear()

            # Emit user message submitted event
            self.event_bus.emit(UserMessageSubmitted(message=user_input))

    def action_clear_input(self) -> None:
        """Clear the input field."""
        if self.input_field:
            self.input_field.clear()
            self.input_field.focus()

    def on_key(self, event: Key) -> None:
        """Handle key events."""
        if event.key == "ctrl+d":
            self.exit()


# Backward compatibility - keep the old class name for any existing imports
# The old TerminantApp was in this file, so we keep it as the main export