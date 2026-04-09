from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal
from app.claude import call_claude

router = APIRouter()

# ── Request / Response Models ──────────────────────────────────────────────

ExplainMode = Literal["interview", "technical", "simple", "pitch"]

class ExplainRequest(BaseModel):
    explanation: str
    mode: ExplainMode = "interview"
    topic: str = ""    # optional: what the explanation is about

class ExplainResponse(BaseModel):
    refined: str
    mode: str

class QuestionsRequest(BaseModel):
    explanation: str
    difficulty: Literal["easy", "medium", "hard"] = "medium"

class QuestionsResponse(BaseModel):
    questions: list[str]

# ── Routes ─────────────────────────────────────────────────────────────────

@router.post("/refine", response_model=ExplainResponse)
async def refine_explanation(req: ExplainRequest):
    """
    Refines a user's explanation based on the selected mode.
    """
    mode_instructions = {
        "interview": """Make this answer concise, structured, and impressive for a technical job interview.
- Use clear structure: what it is → how it works → why it matters
- Be confident and direct
- Keep it under 3 minutes to say out loud
- Use the STAR format if describing a project or experience""",

        "technical": """Make this explanation technically precise and well-structured.
- Use correct technical terminology
- Add implementation details where relevant
- Structure it: overview → how it works → technical details → trade-offs""",

        "simple": """Simplify this so anyone — even a non-technical person — can understand it.
- Use plain language, no jargon
- Use a real-world analogy
- Keep it short: 3-5 sentences max
- Focus on the "why it matters" not the "how it works"  """,

        "pitch": """Turn this into a compelling project or product pitch.
- Lead with the problem being solved
- Clearly state your solution
- Highlight what makes it unique
- End with impact or results
- Keep it punchy and memorable — like a 60-second elevator pitch"""
    }

    topic_line = f"\nTopic: {req.topic}" if req.topic else ""

    prompt = f"""You are a communication and presentation coach.{topic_line}

{mode_instructions[req.mode]}

Original explanation:
\"\"\"{req.explanation}\"\"\"

Return ONLY the refined explanation. No meta-commentary, no labels."""

    result = await call_claude(prompt, max_tokens=800)
    return ExplainResponse(refined=result, mode=req.mode)


@router.post("/questions", response_model=QuestionsResponse)
async def get_interview_questions(req: QuestionsRequest):
    """
    Generates follow-up interview questions based on an explanation.
    """
    difficulty_map = {
        "easy": "basic clarifying questions a junior interviewer might ask",
        "medium": "moderately challenging follow-up questions that probe understanding",
        "hard": "tough, in-depth questions a senior engineer would ask to test deep knowledge"
    }

    prompt = f"""Based on this explanation, generate 5 {difficulty_map[req.difficulty]}.

Explanation:
\"\"\"{req.explanation}\"\"\"

Return a JSON array of exactly 5 question strings. Example format:
["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]

Return ONLY the JSON array. Nothing else."""

    result = await call_claude(prompt, max_tokens=500)

    # Parse the questions from the response
    import json
    import re
    try:
        # Try to extract JSON array from response
        match = re.search(r'\[.*?\]', result, re.DOTALL)
        if match:
            questions = json.loads(match.group())
        else:
            # Fallback: split by newlines
            questions = [
                line.strip().lstrip('0123456789.-) ')
                for line in result.split('\n')
                if line.strip() and '?' in line
            ][:5]
    except Exception:
        questions = [result]

    return QuestionsResponse(questions=questions)
