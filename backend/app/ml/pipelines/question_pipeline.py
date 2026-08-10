import logging
from typing import TypedDict, Optional, List
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END

from backend.app.ml.rag.context_builder import get_full_resume_context
from backend.app.ml.llm.question_generator import generate_questions
from backend.app.db.models.candidate import Candidate
from backend.app.db.models.question import Question
from backend.app.core.logging import get_logger

logger = get_logger("question_pipeline", log_file="logs/question_pipeline.log", level=logging.INFO)


class QuestionState(TypedDict):
    session_id: int
    candidate_id: int
    num_questions: int

    candidate_name: str
    candidate_role: str
    resume_context: str

    questions: Optional[List[dict]]
    saved_count: int

    error: Optional[str]


def fetch_candidate_context_node(state: QuestionState, db: Session) -> QuestionState:
    try:
        candidate = db.query(Candidate).filter(Candidate.id == state["candidate_id"]).first()
        if not candidate:
            logger.error(f"Candidate not found: {state['candidate_id']}")
            return {**state, "error": "Candidate not found"}

        resume_context = get_full_resume_context(db, candidate.id)
        if not resume_context:
            resume_context = candidate.resume_text[:2000] if candidate.resume_text else ""

        return {
            **state,
            "candidate_name": candidate.name,
            "candidate_role": candidate.target_role,
            "resume_context": resume_context,
            "error": None
        }
    except Exception as e:
        logger.error(f"[fetch_candidate_context_node] Error: {e}")
        return {**state, "error": str(e)}


def generate_questions_node(state: QuestionState, db: Session) -> QuestionState:
    if state.get("error"):
        return state
    try:
        questions = generate_questions(
            name=state["candidate_name"],
            role=state["candidate_role"],
            resume_context=state["resume_context"],
            num_questions=state["num_questions"]
        )
        logger.info(f"Generated {len(questions)} questions for candidate {state['candidate_id']}")
        return {**state, "questions": questions, "error": None}
    except Exception as e:
        logger.error(f"[generate_questions_node] Error: {e}")
        return {**state, "questions": [], "error": str(e)}


def save_questions_node(state: QuestionState, db: Session) -> QuestionState:
    if state.get("error") or not state.get("questions"):
        return state

    try:
        questions = state["questions"]
        saved_count = 0

        for idx, q in enumerate(questions):
            question_entry = Question(
                session_id=state["session_id"],
                q_index=idx,
                q_text=q.get("q_text"),
                q_type=q.get("q_type", "technical"),
                topic=q.get("topic")
            )
            db.add(question_entry)
            saved_count += 1

        db.commit()
        logger.info(f"Saved {saved_count} questions for session {state['session_id']}")
        return {**state, "saved_count": saved_count, "error": None}

    except Exception as e:
        db.rollback()
        logger.error(f"[save_questions_node] Error saving questions: {e}")
        return {**state, "saved_count": 0, "error": str(e)}


def build_question_graph(db: Session):
    def _fetch_context(state):      return fetch_candidate_context_node(state, db)
    def _generate_questions(state): return generate_questions_node(state, db)
    def _save_questions(state):     return save_questions_node(state, db)

    graph = StateGraph(QuestionState)
    graph.add_node("fetch_context", _fetch_context)
    graph.add_node("generate_questions", _generate_questions)
    graph.add_node("save_questions", _save_questions)

    graph.set_entry_point("fetch_context")
    graph.add_edge("fetch_context", "generate_questions")
    graph.add_edge("generate_questions", "save_questions")
    graph.add_edge("save_questions", END)

    return graph.compile()


def run_question_pipeline(db: Session, session_id: int, candidate_id: int, num_questions: int = 5) -> dict:
    logger.info(f"Starting question pipeline — session={session_id}, candidate={candidate_id}")

    initial_state: QuestionState = {
        "session_id": session_id,
        "candidate_id": candidate_id,
        "num_questions": num_questions,
        "candidate_name": "",
        "candidate_role": "",
        "resume_context": "",
        "questions": None,
        "saved_count": 0,
        "error": None
    }

    graph = build_question_graph(db)
    result = graph.invoke(initial_state)

    logger.info(f"Question pipeline complete — {result.get('saved_count')} questions saved")
    return result