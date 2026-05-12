import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self, model: str = "gpt-4o"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def get_response(self, prompt: str, system_message: str = "You are Rafeeq, a helpful personal assistant TUI."):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
