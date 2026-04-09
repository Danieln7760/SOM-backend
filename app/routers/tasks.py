from fastapi import APIRouter
from pydantic import BaseModel
from app.claude import call_claude

router = APIRouter()

# ── Request / Response Models ──────────────────────────────────────────────

class PrioritizeRequest(BaseModel):
    tasks: str          # raw comma-separated or freeform task input

class BreakdownRequest(BaseModel):
    tasks: str          # one or more tasks to break down
    context: str = ""   # optional extra context (e.g. "I have a job interview tomorrow")

class TaskResponse(BaseModel):
    result: str
    raw_input: str

# ── Routes ─────────────────────────────────────────────────────────────────

@router.post("/prioritize", response_model=TaskResponse)
async def prioritize_tasks(req: PrioritizeRequest):
    """
    Takes a freeform list of tasks and returns an AI-prioritized breakdown.
    """
    prompt = f"""You are a productivity AI assistant. The user gave you these tasks:

"{req.tasks}"

For each task:
1. Assign priority: HIGH / MEDIUM / LOW
2. Estimate time required (e.g. 30 min, 2 hrs)
3. Give one concrete, specific next step to get started
4. Suggest the best time of day to tackle it

Then at the end suggest an optimal order to complete all tasks today.

Be direct, practical, and concise. Use clear formatting."""

    result = await call_claude(prompt, max_tokens=900)
    return TaskResponse(result=result, raw_input=req.tasks)


@router.post("/breakdown", response_model=TaskResponse)
async def breakdown_task(req: BreakdownRequest):
    """
    Takes a task (or multiple tasks) and breaks it into detailed steps.
    """
    context_line = f"\nExtra context: {req.context}" if req.context else ""

    prompt = f"""You are a productivity AI. Break down the following task(s) into clear, actionable steps:

"{req.tasks}"{context_line}

For each task provide:
- Priority level (HIGH / MEDIUM / LOW)
- Estimated total time
- 3-5 concrete steps to complete it
- Any tools, resources, or preparation needed
- A realistic deadline suggestion

Format cleanly and be specific. No vague advice."""

    result = await call_claude(prompt, max_tokens=1000)
    return TaskResponse(result=result, raw_input=req.tasks)
