"""Suggestions widget for command autocomplete in Terminant TUI."""

from textual.containers import Container
from textual.widgets import ListView, ListItem, Label
from textual.reactive import reactive
from textual.message import Message
from textual.events import Key
from tools.base import Tool


class SuggestionsWidget(Container):
    """A widget that displays command suggestions above the input area."""

    DEFAULT_CSS = """
    SuggestionsWidget {
        height: auto;
        max-height: 15;
        width: 100%;
        display: none;
        border: solid $primary;
        background: $surface;
        margin: 0 1 1 1;
        padding: 0 1;
    }

    SuggestionsWidget.visible {
        display: block;
    }

    #suggestions-list {
        height: auto;
        max-height: 12;
    }

    #suggestions-list > ListItem {
        height: 1;
        padding: 0 1;
    }

    #suggestions-list > ListItem.-highlighted {
        background: $accent;
        color: $text;
    }

    .suggestion-name {
        color: $primary;
        text-style: bold;
        width: 12;
    }

    .suggestion-description {
        color: $text-muted;
        width: 1fr;
    }
    """

    # Reactive state
    suggestions_visible = reactive(False)
    current_filter = reactive("")
    selected_index = reactive(0)

    def __init__(self, runtime_tools: dict[str, Tool] | None = None, **kwargs):
        super().__init__(**kwargs)
        self._suggestions_list = ListView(id="suggestions-list")
        self._runtime_tools = runtime_tools or {}
        self._matching_tools: list[Tool] = []

    def compose(self):
        yield self._suggestions_list

    def watch_suggestions_visible(self, visible: bool) -> None:
        """React to visibility changes."""
        if visible:
            self.add_class("visible")
            self._update_suggestions_list()
        else:
            self.remove_class("visible")
            self._suggestions_list.clear()
            self.selected_index = 0

    def watch_current_filter(self, filter_text: str) -> None:
        """React to filter changes."""
        self._update_suggestions_list()

    def _update_suggestions_list(self) -> None:
        """Update the suggestions list based on current filter."""
        if not self.suggestions_visible:
            return

        # Find matching tools
        self._matching_tools = self._find_matching_tools(self.current_filter)

        # Clear and repopulate list
        self._suggestions_list.clear()

        for tool in self._matching_tools:
            item = ListItem(
                Label(f"/{tool.name:<11} {tool.description}", classes="suggestion-item"),
                classes="suggestion-item"
            )
            self._suggestions_list.append(item)

        # Reset selection
        if self._matching_tools:
            self.selected_index = 0
            if len(self._suggestions_list.children) > 0:
                self._suggestions_list.index = 0

    def _find_matching_tools(self, prefix: str) -> list[Tool]:
        """Find tools matching the given prefix."""
        if not prefix.startswith('/'):
            prefix = '/' + prefix

        # Remove the leading / for matching
        search_prefix = prefix[1:].lower()

        matches = []
        for tool in self._runtime_tools.values():
            if tool.name.lower().startswith(search_prefix):
                matches.append(tool)
        return matches

    def set_runtime_tools(self, runtime_tools: dict[str, Tool]) -> None:
        """Update the runtime tools registry."""
        self._runtime_tools = runtime_tools
        if self.suggestions_visible:
            self._update_suggestions_list()

    def show_for_input(self, input_text: str) -> None:
        """Show suggestions based on input text."""
        if input_text.startswith('/'):
            self.current_filter = input_text
            self.suggestions_visible = True
        else:
            self.suggestions_visible = False

    def hide(self) -> None:
        """Hide the suggestions."""
        self.suggestions_visible = False

    def get_selected_tool(self) -> Tool | None:
        """Get the currently selected tool."""
        if self._matching_tools and 0 <= self.selected_index < len(self._matching_tools):
            return self._matching_tools[self.selected_index]
        return None

    def action_move_up(self) -> None:
        """Move selection up."""
        if self._matching_tools:
            self.selected_index = (self.selected_index - 1) % len(self._matching_tools)
            self._suggestions_list.index = self.selected_index

    def action_move_down(self) -> None:
        """Move selection down."""
        if self._matching_tools:
            self.selected_index = (self.selected_index + 1) % len(self._matching_tools)
            self._suggestions_list.index = self.selected_index

    def action_select(self) -> Tool | None:
        """Select the current tool."""
        return self.get_selected_tool()

    def on_key(self, event: Key) -> None:
        """Handle key events when suggestions are visible."""
        if not self.suggestions_visible:
            return

        if event.key == "up":
            event.stop()
            self.action_move_up()
        elif event.key == "down":
            event.stop()
            self.action_move_down()
        elif event.key == "enter":
            event.stop()
            tool = self.action_select()
            if tool:
                self.post_message(self.ToolSelected(tool))
        elif event.key == "escape":
            event.stop()
            self.hide()
            self.post_message(self.Dismissed())

    class ToolSelected(Message):
        """Message posted when a tool is selected."""
        def __init__(self, tool: Tool) -> None:
            self.tool = tool
            super().__init__()

    class Dismissed(Message):
        """Message posted when suggestions are dismissed."""
        pass