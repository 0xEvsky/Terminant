import sys
import threading
import re
from events.event_bus import EventBus
from events.agent_events import UserMessageSubmitted, AssistantMessageFinished, StreamingToken, ConversationLoaded, AgentIdle
from rich.console import Console
from rich.text import Text


class TerminantApp:
    """The root UI application. Owns the event loop and widget tree."""

    def __init__(self, event_bus: EventBus, memory_store=None, **kwargs):
        self.event_bus = event_bus
        self.memory_store = memory_store
        self.console = Console()
        self.agent_idle_event = threading.Event()
        self.agent_idle_event.set()  # Start idle
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Set up event subscriptions for the UI."""
        self.event_bus.subscribe(AssistantMessageFinished, self._on_assistant_message)
        self.event_bus.subscribe(StreamingToken, self._on_streaming_token)
        self.event_bus.subscribe(AgentIdle, self._on_agent_idle)

    def _on_agent_idle(self, event: AgentIdle):
        """Handle agent idle event."""
        self.agent_idle_event.set()

    def _on_assistant_message(self, event: AssistantMessageFinished):
        """Handle assistant message finished event by printing the message with styling."""
        # Filter out model formatting markers that aren't needed in terminal
        filtered_message = self._filter_model_formatting(event.message)

        # Print a newline before the assistant message to separate from previous content
        self.console.print()
        # Print the message with bold and a dot prefix
        text = Text("• ", style="bold") + Text(filtered_message)
        self.console.print(text)
        # Print a newline after the message to separate from next prompt
        self.console.print()

    def _on_streaming_token(self, event: StreamingToken):
        """Handle streaming token event by printing the token without newline."""
        self.console.print(event.token, end="")

    def _filter_model_formatting(self, text: str) -> str:
        """
        Filter out model formatting markers like **, *, '', `` that are used for
        formatting but not needed in terminal output.
        """
        if not isinstance(text, str):
            return text

        # Remove bold formatting: **text** or __text__
        # Using regex to match pairs
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'__(.*?)__', r'\1', text)

        # Remove italic formatting: *text* or _text_
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'_(.*?)_', r'\1', text)

        # Remove inline code formatting: `text`
        text = re.sub(r'`(.*?)`', r'\1', text)

        # Remove ''text'' formatting (not sure what this is for, but user mentioned it)
        text = re.sub(r"''(.*?)''", r'\1', text)

        return text

    def _get_styled_user_input(self, prompt: str = "> ") -> str:
        """
        Get user input with prompt, then style the input line with grey background.
        Returns the input string (without trailing newline).
        """
        # Write prompt without newline, flush to ensure it appears
        sys.stdout.write(prompt)
        sys.stdout.flush()

        # Read line from stdin (terminal will echo as user types)
        line = sys.stdin.readline()

        # Remove trailing newline for processing
        if line.endswith('\n'):
            line = line[:-1]
        elif line.endswith('\r\n'):
            line = line[:-2]

        user_input = line

        # Clear the echoed input line and re-print with styling
        # Move cursor up one line and clear it
        sys.stdout.write('\x1b[1A\x1b[2K')
        sys.stdout.flush()

        # Print the styled user message: grey background and "> " prefix
        # We want the highlight to extend to full width, so we'll pad with spaces
        console_width = self.console.size.width
        prompt_width = len(prompt)
        # Calculate how much space we need for the grey background
        # We want it to extend to the end of the line
        grey_background = " " * (console_width - prompt_width)

        # Create the styled text: "> " prefix + user input + padding for full-width grey background
        # The grey background style will apply to the entire string
        content = "> " + user_input + grey_background
        text = Text(content, style="on #3a3a3a")
        # Use console to print with proper styling
        self.console.print(text)

        # Print an additional newline to create a blank line before the assistant's message
        self.console.print()

        return user_input

    def run(self):
        """Run the app in inline mode, printing conversation directly to terminal."""
        # Print separator line to distinguish chat area from prompting area
        console_width = self.console.size.width
        separator_line = "─" * console_width
        self.console.print(separator_line)

        # Emit conversation loaded event (empty history for now)
        self.event_bus.emit(ConversationLoaded(messages=[]))

        # Add colored squares above welcome message - left square bigger than right, both squares, no space between
        # Make left square bigger in both height and width, and still be a square
        left_size = 4   # 4x4 square (bigger)
        right_size = 2  # 2x2 square (smaller)

        # Generate lines for each square
        left_lines = []
        for i in range(left_size):
            line = Text(" " * left_size, style="on #fff7d1")
            left_lines.append(line)

        right_lines = []
        for i in range(right_size):
            line = Text(" " * right_size, style="on #8b5dff")
            right_lines.append(line)

        # Print squares side by side with bottom alignment, no space between
        # Total height is max(left_size, right_size) = left_size (since left_size >= right_size)
        for line_idx in range(left_size):
            # Get left square line (always available since we're iterating through its height)
            left_line = left_lines[line_idx]

            # Calculate right square line index for bottom alignment
            # When line_idx = left_size - 1 (bottom line), we want right_size - 1 (bottom line of right square)
            right_line_idx = line_idx - (left_size - right_size)

            if 0 <= right_line_idx < right_size:
                right_line = right_lines[right_line_idx]
                # Print left line and right line with no space between
                self.console.print(left_line, right_line, sep="")
            else:
                # Right square not visible on this line (above where it starts)
                # Print left line with empty space for right square width
                empty_space = Text(" " * right_size)
                self.console.print(left_line, empty_space, sep="")

        # Print welcome message
        self.console.print("Terminant - Type your message and press Enter to send.")
        self.console.print("Type '/exit' or press Ctrl+D to quit.")
        self.console.print()

        # Main loop
        while True:
            try:
                # Wait for agent to be idle before prompting for input
                self.agent_idle_event.wait()
                # Clear the idle event while we wait for the next response
                self.agent_idle_event.clear()

                # Print separator line before each prompt
                console_width = self.console.size.width
                separator_line = "─" * console_width
                self.console.print(separator_line)

                # Get styled user input
                user_input = self._get_styled_user_input("> ")
            except EOFError:
                # Ctrl+D
                self.console.print()  # Newline for clean exit
                break

            # Check for exit command
            if user_input.strip() == "/exit":
                break

            # Emit user message submitted event
            self.event_bus.emit(UserMessageSubmitted(message=user_input))
            # The agent will process and emit AgentBusy, then eventually AgentIdle.
            # We will wait for AgentIdle in the next loop iteration.

        # Loop ended
        self.console.print("Goodbye!")