class Memory:
    def __init__(self):
        self.messages = []

    def add_system_message(self, content):
            self.messages.append({
                "role": "system",
                "content": content
            })

    def add_user_message(self, content):
        self.messages.append({
            "role": "user",
            "content": content
        })

    def add_assistant_message(self, content):
        self.messages.append({
            "role": "assistant",
            "content": content
        })


    def add_tool_call(self, id, name, arguments, type='function'):
        self.messages.append({
            "role": "assistant",
            "tool_calls": [
                {
                    "id": id,
                    "type": type,
                    "function": 
                    {
                        "name": name,
                        "arguments": arguments
                    }
                }
            ]
        })

    def add_tool_result(self, tool_call_id, content):
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content
        })

    def get_messages(self):
        return self.messages