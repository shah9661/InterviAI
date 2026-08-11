import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db.database import init_db
from backend.app.core.config import settings
from backend.app.core.logging import get_logger

from backend.app.api.v1 import auth, candidates, interviews, questions, answers, reports

logger = get_logger("main", log_file="logs/app.log", level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("Starting up InterviAI backend...")
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down InterviAI backend...")


app = FastAPI(
    title="InterviAI",
    description="AI-powered mock interview platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500","http://localhost:5500",], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(candidates.router)
app.include_router(interviews.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {"message": "InterviAI backend is running", "status": "healthy"}


@app.get("/health")
def health_check():
    return {"status": "ok"}