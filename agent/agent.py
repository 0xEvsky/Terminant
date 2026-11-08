import json
import threading
from llm.client import LLMClient
from agent.memory import Memory
from llm.prompts import SYSTEM_PROMPT
from logger import log_error, log_info
from tools.registry import ToolNotFoundError, get_tool
from tools.base import Tool, ToolResult
from events.agent_events import (
    AgentEvent,
    ToolCallFailed,
    APICallFailed,
    UserMessageSubmitted,
    AgentBusy,
    AgentIdle,
    AssistantMessageFinished,
    ToolStarted,
    ToolFinished )
from events.event_bus import EventBus


class Agent:
    def __init__(self, client: LLMClient, event_bus: EventBus):
        self.client: LLMClient = client
        self.memory = Memory()
        self.memory.add_system_message(SYSTEM_PROMPT)
        self.agent_mode = False
        self.event_bus = event_bus

        self.event_bus.subscribe(UserMessageSubmitted, self._on_message_submit)

    def emit(self, event: AgentEvent):
        self.event_bus.emit(event)

    def _on_message_submit(self, event: UserMessageSubmitted):
        message = event.message
        log_info(f"User: {message}")
        thread = threading.Thread(
            target=self._process_message_background,
            args=(message, ),
            daemon=True
        )
        thread.start()

    def _process_message_background(self, message: str):
        if message:
            self.memory.add_user_message(message)
            if message == '/agent':
                self.agent_mode = True

            elif message == '/chat':
                self.agent_mode = False

            elif message == '/':
                self.agent_mode = False
                self.event_bus.emit(AgentIdle())
                return ''

        self.event_bus.emit(AgentBusy())

        try:
            while True:
                log_info("Sending messages to model")

                model_response = self.client.chat(messages=self.memory.get_messages())
                log_info("Model responded")

                if isinstance(model_response, str):
                    self.memory.add_assistant_message(model_response)
                    self.event_bus.emit(AssistantMessageFinished(message=model_response))
                    log_info("Final response generated")
                    return model_response

                if model_response.tool_calls:
                    self.handle_tool_calls(model_response.tool_calls)
                    continue

                response = model_response.content
                self.memory.add_assistant_message(response)
                self.emit(AssistantMessageFinished(message=response))

                log_info("Final response generated")
                return response
        except Exception as e:
            self.emit(APICallFailed(error=str(e)))
            log_error(f"Unable to call model API: {e}")

        finally:
            self.event_bus.emit(AgentIdle())

    def handle_tool_calls(self, tool_calls):
        for tool_call in tool_calls:
            self.handle_tool_call(tool_call)

    def handle_tool_call(self, tool_call):
        tool_call_id = tool_call.id
        tool_name = tool_call.function.name

        try:
            arguments = json.loads(tool_call.function.arguments)
            
        except json.JSONDecodeError as e:
            log_error(f"Invalid JSON in tool call arguments: {e}")
            self.emit(ToolCallFailed(tool_name=tool_name, error=f"Invalid JSON in tool call arguments: {e}"))
            return

        self.memory.add_tool_call(id=tool_call_id, name=tool_name, arguments=tool_call.function.arguments)

        log_info(f'called tool: {tool_name}')
        log_info(f'arguments: {arguments}')

        result = ToolResult(False, output="", error="Tool execution failed")

        if tool_name == 'agent_check_mode':
            result = self.check_agent_mode()

        elif self.agent_mode:
            try:
                tool:Tool = get_tool(tool_name)
                if not tool:
                    raise ToolNotFoundError(f"Tool '{tool_name}' not found in registry")
                tool.validate_arguments(arguments) # raises ValueError if arguments are invalid
                self.emit(ToolStarted(tool=tool))
                result = tool.execute(**arguments)
                self.emit(ToolFinished(tool=tool))

            except ToolNotFoundError as e:
                log_error(e)
                result = ToolResult(False, output=str(e), error=str(e))
                self.emit(ToolCallFailed(tool_name=tool_name, error=str(e)))

            except Exception as e:
                log_error(e)
                result = ToolResult(
                    False, 
                    output=f"Tool execution failed: {str(e)}", 
                    error=str(e))
                self.emit(ToolCallFailed(tool_name=tool_name, error=str(e)))

        else:
            result.output = ""
            result.error = "Agent mode is disabled"
            self.emit(ToolCallFailed(tool_name=tool_name, error="Agent mode is disabled"))

        self.memory.add_tool_result(
            tool_call_id=tool_call_id,
            content=json.dumps(result.to_dict()),
        )

    def check_agent_mode(self) -> dict:
        return ToolResult(True, output={"agent_mode": self.agent_mode})