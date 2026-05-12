import os
from openai import APIStatusError, AuthenticationError, OpenAI, RateLimitError
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self, model: str | None = None):
        self.base_url = os.getenv("OPENAI_BASE_URL")
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
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")

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
        except RateLimitError as e:
            error_code = getattr(e, "code", None)
            message = getattr(e, "message", str(e))
            if error_code == "insufficient_quota":
                return (
                    "OpenAI quota error: this API key's project is out of credits or has hit "
                    "its monthly spend limit. Check that OPENAI_PROJECT_ID points to the project "
                    f"with available API quota. Details: {message}"
                )
            return f"OpenAI rate limit error: {message}"
        except AuthenticationError as e:
            message = getattr(e, "message", str(e))
            return f"OpenAI authentication error: check OPENAI_API_KEY. Details: {message}"
        except APIStatusError as e:
            message = getattr(e, "message", str(e))
            return f"OpenAI API error ({e.status_code}): {message}"
        except Exception as e:
            return f"Error: {str(e)}"
