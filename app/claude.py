import os
import anthropic
from fastapi import HTTPException

# Initialize the Anthropic client
# It automatically reads ANTHROPIC_API_KEY from environment
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-20250514"

async def call_claude(prompt: str, max_tokens: int = 1000, system: str = None) -> str:
    """
    Call the Claude API with a prompt and return the response text.
    """
    try:
        kwargs = {
            "model": MODEL,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system:
            kwargs["system"] = system

        message = client.messages.create(**kwargs)
        return message.content[0].text

    except anthropic.AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key. Check your ANTHROPIC_API_KEY environment variable."
        )
    except anthropic.RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Rate limit reached. Please try again in a moment."
        )
    except anthropic.APIError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Claude API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
