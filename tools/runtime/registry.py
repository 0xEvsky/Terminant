"""Runtime tools registry factory for Terminant.

This module provides a factory function to create and initialize
all runtime tools with their dependencies.
"""

from tools.base import Tool
from tools.runtime.switch_mode import SwitchMode
from events.event_bus import EventBus


def create_runtime_tools(event_bus: EventBus) -> dict[str, Tool]:
    """Create and return the runtime tools registry.

    Args:
        event_bus: The event bus for tools to emit events.

    Returns:
        A dictionary mapping tool names to tool instances.
    """
    tools: list[Tool] = [
        SwitchMode(event_bus),
        # Add other runtime tools here as they are implemented
    ]

    return {tool.name: tool for tool in tools}