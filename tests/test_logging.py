from agent.agent import Agent
from tools.filesystem.list_files import ListFiles


class FakeClient:
    def chat(self, messages):
        return "fake response"


def test_agent_logs_key_events(capsys):
    agent = Agent(FakeClient())

    agent.step("Show me files")

    captured = capsys.readouterr().out
    assert "[INFO] User: Show me files" in captured
    assert "[INFO] Sending" in captured
    assert "[INFO] Model responded" in captured
    assert "[INFO] Final response generated" in captured


def test_tool_logs_execution(capsys):
    tool = ListFiles()

    result = tool.execute(path=".")

    captured = capsys.readouterr().out
    assert "[INFO] Executing filesystem.list_files(path='.')" in captured
    assert "[INFO] Tool returned" in captured
    assert isinstance(result, list)
