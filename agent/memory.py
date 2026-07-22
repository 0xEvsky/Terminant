class Memory:
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            }
        ]

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

    def get_messages(self):
        return self.messages