from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tasks, messages, explain, summary, voice

app = FastAPI(
    title="DailyFlow AI API",
    description="AI-powered personal workflow assistant backend",
    version="1.0.0"
)

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: replace with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(tasks.router,    prefix="/api/tasks",    tags=["Tasks"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(explain.router,  prefix="/api/explain",  tags=["Explain"])
app.include_router(summary.router,  prefix="/api/summary",  tags=["Summary"])
app.include_router(voice.router,    prefix="/api/voice",    tags=["Voice"])

@app.get("/")
def root():
    return {
        "app": "DailyFlow AI",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
