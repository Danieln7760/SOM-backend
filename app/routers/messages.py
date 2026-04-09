from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal
from app.claude import call_claude

router = APIRouter()

# ── Request / Response Models ──────────────────────────────────────────────

ToneType = Literal["professional", "friendly", "concise", "formal", "persuasive", "casual"]

class ImproveRequest(BaseModel):
    message: str
    tone: ToneType = "professional"
    message_type: str = "email"   # email, slack, explanation, etc.

class ImproveResponse(BaseModel):
    improved: str
    feedback: str
    tone: str

class SubjectRequest(BaseModel):
    message: str   # email body to generate subject for

class SubjectResponse(BaseModel):
    subject: str

# ── Routes ─────────────────────────────────────────────────────────────────

@router.post("/improve", response_model=ImproveResponse)
async def improve_message(req: ImproveRequest):
    """
    Rewrites a message with the specified tone.
    Also returns brief feedback on what was changed.
    """
    improve_prompt = f"""You are a professional communication expert. Rewrite the following {req.message_type} to be {req.tone}.

Original message:
\"\"\"{req.message}\"\"\"

Rules:
- Match the requested tone: {req.tone}
- Fix grammar and clarity issues
- Make it more concise if needed
- Preserve the core meaning and intent
- Do NOT add filler phrases like "I hope this finds you well"

Return ONLY the improved {req.message_type}. No explanations, no labels."""

    feedback_prompt = f"""Briefly analyze what was improved in this message rewrite. Give exactly 3 bullet points.
Focus on: clarity, tone, structure, grammar, conciseness.

Original: \"\"\"{req.message[:300]}\"\"\"

Be very concise — one short sentence per bullet."""

    # Run both in sequence
    improved = await call_claude(improve_prompt, max_tokens=800)
    feedback = await call_claude(feedback_prompt, max_tokens=300)

    return ImproveResponse(
        improved=improved,
        feedback=feedback,
        tone=req.tone
    )


@router.post("/subject", response_model=SubjectResponse)
async def generate_subject(req: SubjectRequest):
    """
    Generates a compelling email subject line from the email body.
    """
    prompt = f"""Generate a clear, professional email subject line for this email body.

Email:
\"\"\"{req.message[:500]}\"\"\"

Return ONLY the subject line. No quotes, no labels, just the subject."""

    result = await call_claude(prompt, max_tokens=60)
    return SubjectResponse(subject=result.strip())
