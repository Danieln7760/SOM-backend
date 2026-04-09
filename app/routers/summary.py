from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.claude import call_claude

router = APIRouter()

# ── Request / Response Models ──────────────────────────────────────────────

class Task(BaseModel):
    text: str
    done: bool
    priority: str = "med"

class SummaryRequest(BaseModel):
    description: str           # what the user did today (freeform)
    tasks: Optional[list[Task]] = []   # task list from the app
    date: Optional[str] = ""   # e.g. "Monday, April 8"

class SummarySection(BaseModel):
    title: str
    content: str
    emoji: str

class SummaryResponse(BaseModel):
    sections: list[SummarySection]
    motivation: str
    focus_score: int   # 0-100

# ── Routes ─────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=SummaryResponse)
async def generate_summary(req: SummaryRequest):
    """
    Generates a structured daily summary with insights and recommendations.
    """
    # Build task context
    task_context = ""
    if req.tasks:
        done = [t.text for t in req.tasks if t.done]
        pending = [t.text for t in req.tasks if not t.done]
        task_context = f"""
Tasks completed: {', '.join(done) if done else 'none'}
Tasks still pending: {', '.join(pending) if pending else 'none'}"""

    date_line = f"Date: {req.date}" if req.date else ""

    prompt = f"""You are a personal productivity coach analyzing someone's day.
{date_line}

What they did today:
\"\"\"{req.description}\"\"\"{task_context}

Give a structured daily summary as a JSON object with this exact format:
{{
  "accomplishments": "bullet points of what went well today",
  "pending": "what still needs attention tomorrow",
  "insights": "2-3 patterns or observations about their productivity",
  "tomorrow": "3 specific, actionable recommendations for tomorrow",
  "motivation": "one short encouraging sentence (max 20 words)",
  "focus_score": <integer 0-100 based on productivity described>
}}

Be specific, practical, and encouraging. Return ONLY valid JSON."""

    result = await call_claude(prompt, max_tokens=900)

    # Parse JSON response
    import json
    import re
    try:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        data = json.loads(match.group()) if match else json.loads(result)
    except Exception:
        # Fallback structure if JSON parsing fails
        data = {
            "accomplishments": result,
            "pending": "Review your tasks for tomorrow",
            "insights": "Keep building consistent habits",
            "tomorrow": "Start with your highest priority task",
            "motivation": "Every day of effort compounds into something great.",
            "focus_score": 70
        }

    sections = [
        SummarySection(title="Accomplishments", content=data.get("accomplishments", ""), emoji="✅"),
        SummarySection(title="Still Pending", content=data.get("pending", ""), emoji="⏳"),
        SummarySection(title="Insights", content=data.get("insights", ""), emoji="💡"),
        SummarySection(title="Tomorrow's Plan", content=data.get("tomorrow", ""), emoji="🚀"),
    ]

    return SummaryResponse(
        sections=sections,
        motivation=data.get("motivation", "Keep going — you're building something great."),
        focus_score=int(data.get("focus_score", 70))
    )
