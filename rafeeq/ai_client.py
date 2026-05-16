import os
from typing import List, Dict, Any, Optional
from openai import APIStatusError, AuthenticationError, OpenAI, RateLimitError
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self, model: str | None = None):
        self.base_url = os.getenv("AI_BASE_URL") or os.getenv("OPENAI_BASE_URL")
        is_gemini = bool(self.base_url and "generativelanguage.googleapis.com" in self.base_url)
        self.api_key = os.getenv("GEMINI_API_KEY") if is_gemini else os.getenv("OPENAI_API_KEY")
        self.api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError("API key not found. Set GEMINI_API_KEY for Gemini or OPENAI_API_KEY for OpenAI.")
        self.organization = os.getenv("OPENAI_ORG_ID") or os.getenv("OPENAI_ORGANIZATION")
        self.project = os.getenv("OPENAI_PROJECT_ID")
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        if not is_gemini:
            client_kwargs["organization"] = self.organization
            client_kwargs["project"] = self.project
        self.client = OpenAI(**client_kwargs)
        self.provider_name = "Gemini" if is_gemini else "OpenAI"
        self.model = model or os.getenv("AI_MODEL") or os.getenv("OPENAI_MODEL", "gemini-2.5-flash" if is_gemini else "gpt-4o")
        self.history = []

    def get_response(self, prompt: Optional[str], system_message: str = "You are Rafeeq, a helpful personal assistant TUI."):
        if prompt:
            self.history.append({"role": "user", "content": prompt})
        
        try:
            messages = [{"role": "system", "content": system_message}] + self.history
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            content = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": content})
            return content
        except RateLimitError as e:
            error_code = getattr(e, "code", None)
            message = getattr(e, "message", str(e))
            if error_code == "insufficient_quota":
                return (
                    f"{self.provider_name} quota error: this API key is out of credits, "
                    f"rate-limited, or not enabled for this model. Details: {message}"
                )
            return f"{self.provider_name} rate limit error: {message}"
        except AuthenticationError as e:
            message = getattr(e, "message", str(e))
            return f"{self.provider_name} authentication error: check the API key in .env. Details: {message}"
        except APIStatusError as e:
            message = getattr(e, "message", str(e))
            return f"{self.provider_name} API error ({e.status_code}): {message}"
        except Exception as e:
            return f"Error: {str(e)}"

    def add_observation(self, observation: str):
        self.history.append({"role": "user", "content": f"OBSERVATION: {observation}"})

    def clear_history(self):
        self.history = []
