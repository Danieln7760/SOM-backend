from fastapi import APIRouter
from pydantic import BaseModel
from app.claude import call_claude

router = APIRouter()

# ── Request / Response Models ──────────────────────────────────────────────

class VoiceRequest(BaseModel):
    transcript: str      # the spoken text (from speech-to-text)
    context: str = ""    # optional: what the user is working on

class ActionItem(BaseModel):
    task: str
    priority: str        # HIGH / MEDIUM / LOW
    deadline: str        # e.g. "Today", "Tomorrow", "This week"
    steps: list[str]

class VoiceResponse(BaseModel):
    action_items: list[ActionItem]
    summary: str
    prep_plan: str

# ── Routes ─────────────────────────────────────────────────────────────────

@router.post("/process", response_model=VoiceResponse)
async def process_voice(req: VoiceRequest):
    """
    Converts a spoken transcript into structured tasks and an action plan.
    """
    context_line = f"\nContext: {req.context}" if req.context else ""

    prompt = f"""You are a productivity AI. Convert this spoken thought into a structured action plan.{context_line}

Transcript: \"\"\"{req.transcript}\"\"\"

Return a JSON object with this exact format:
{{
  "action_items": [
    {{
      "task": "clear task name",
      "priority": "HIGH" or "MEDIUM" or "LOW",
      "deadline": "Today" or "Tomorrow" or "This week" or specific date,
      "steps": ["step 1", "step 2", "step 3"]
    }}
  ],
  "summary": "one sentence summarizing what needs to be done",
  "prep_plan": "a short paragraph with the recommended approach and order"
}}

Extract all tasks mentioned. Be specific and actionable.
Return ONLY valid JSON."""

    result = await call_claude(prompt, max_tokens=900)

    # Parse JSON
    import json
    import re
    try:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        data = json.loads(match.group()) if match else json.loads(result)

        action_items = [
            ActionItem(
                task=item.get("task", ""),
                priority=item.get("priority", "MEDIUM"),
                deadline=item.get("deadline", "Today"),
                steps=item.get("steps", [])
            )
            for item in data.get("action_items", [])
        ]

        return VoiceResponse(
            action_items=action_items,
            summary=data.get("summary", ""),
            prep_plan=data.get("prep_plan", "")
        )

    except Exception:
        # Fallback if JSON parsing fails
        return VoiceResponse(
            action_items=[ActionItem(
                task=req.transcript[:100],
                priority="MEDIUM",
                deadline="Today",
                steps=["Review the task", "Break it into steps", "Get started"]
            )],
            summary="Task extracted from voice input",
            prep_plan=result
        )
