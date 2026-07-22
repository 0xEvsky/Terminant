from openai import OpenAI

class LLMClient:
    def __init__(self, api_key=None, model="nvidia/nemotron-3-ultra-550b-a55b:free"):
        self.api_key = api_key
        self.model = model

    def chat(self, prompt):
        if not prompt:
            raise ValueError("no prompt has been provided")

        if not self.api_key:
            return "LLM not configured: set OPENROUTER_API_KEY to enable API calls."

        return self._call_api(prompt)

    def _call_api(self, prompt):
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

