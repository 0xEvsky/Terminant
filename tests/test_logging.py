import sys
from agent.agent import Agent
from tools.filesystem.list_files import ListFiles
from events.event_bus import EventBus
from logger import set_stream


class FakeClient:
    def chat(self, messages):
        return "fake response"


def test_agent_logs_key_events(capsys):
    # Set logger stream to stdout so capsys can capture it
    set_stream(sys.stdout)

    event_bus = EventBus()
    agent = Agent(FakeClient(), event_bus)

    # Emit user message to trigger processing
    from events.agent_events import UserMessageSubmitted
    agent.event_bus.emit(UserMessageSubmitted(message="Show me files"))

    # Wait for background thread to complete
    import time
    time.sleep(0.5)

    output = capsys.readouterr()
    captured = output.out + output.err
    # Log format: [timestamp] [LEVEL] [caller] message
    assert "User: Show me files" in captured
    assert "Sending messages to model" in captured
    assert "Model responded" in captured
    assert "Final response generated" in captured

    # Restore stream
    set_stream(None)


def test_tool_logs_execution(capsys):
    # Set logger stream to stdout so capsys can capture it
    set_stream(sys.stdout)

    tool = ListFiles()

    result = tool.execute(path=".")

    output = capsys.readouterr()
    captured = output.out + output.err
    assert "Executing filesystem_list_files(path='.')" in captured
    assert "Tool returned" in captured
    assert result.success
    assert isinstance(result.output, list)

    # Restore stream
    set_stream(None)
