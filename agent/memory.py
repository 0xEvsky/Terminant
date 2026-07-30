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


    def add_tool_result(self, content):
        self.messages.append({
            "role": "tool",
            "content": content
        })

    def get_messages(self):
        return self.messages