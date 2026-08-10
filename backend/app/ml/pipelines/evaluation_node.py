import logging
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.db.models.answer import Answer
from backend.app.db.models.evaluation import Evaluation, EvaluationRating
from backend.app.db.models.question import Question
from backend.app.db.models.interview import InterviewSession, InterviewStatus
from backend.app.db.models.candidate import Candidate
from backend.app.db.models.report import OverallReport
from backend.app.ml.rag.retriever import search_similar_chunk
from backend.app.ml.llm.evaluator import evaluate_answer, generate_overall_report
from backend.app.core.logging import get_logger
from backend.app.ml.pipelines.evaluation_state import EvaluationState

logger = get_logger("evaluation_nodes", log_file="logs/evaluation_node.log", level=logging.INFO)


def fetch_context(state: EvaluationState, db: Session) -> EvaluationState:
    try:
        question = db.query(Question).filter(Question.id == state["question_id"]).first()  # question fetch
        session = db.query(InterviewSession).filter(InterviewSession.id == state["session_id"]).first() # session fetch

        if not question or not session:
            logger.error(f"Question or session not found — q_id={state['question_id']}, s_id={state['session_id']}")
            return {**state, "error": "Question or session not found"}

        candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first() # candidate fetch
        if not candidate:
            logger.error(f"Candidate not found for session {session.id}")
            return {**state, "error": "Candidate not found"}

        similar_chunks = search_similar_chunk(db=db, candidate_id=candidate.id, query=question.q_text, top_k=3) # find similar

        resume_context = "\n\n".join([
            f"[Relevance: {c['similarity']}]\n{c['chunk_text']}" for c in similar_chunks
        ])
        if not resume_context:
            resume_context = candidate.resume_text[:2000]

        return {
            **state,
            "candidate_name": candidate.name,
            "candidate_role": candidate.target_role,
            "question_text": question.q_text,
            "resume_context": resume_context,
            "error": None
        }
    except Exception as e:
        logger.error(f"[fetch_context] Error: {e}")
        return {**state, "error": str(e)}


def evaluate_answer_node(state: EvaluationState, db: Session) -> EvaluationState:
    if state.get("error"):
        return state
    logger.info("Evaluating answer with LLM...")
    try:
        result = evaluate_answer(
            name=state["candidate_name"], role=state["candidate_role"],
            resume_context=state["resume_context"], question=state["question_text"],
            answer=state["transcript"]
        )
        return {
            **state,
            "score": result.get("score", 0),
            "rating": result.get("rating", "Average"),
            "feedback": result.get("feedback", ""),
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", []),
        }
    except Exception as e:
        logger.error(f"[evaluate_answer_node] Error: {e}")
        return {
            **state, "score": 5, "rating": "Average",
            "feedback": "Evaluation could not be completed.",
            "strengths": [], "improvements": [], "error": str(e)
        }


def save_evaluation(state: EvaluationState, db: Session) -> EvaluationState:
    if state.get("error"):
        return state
    logger.info(f"Saving evaluation — Score: {state['score']}/10")
    try:
        rating_map = {
            "Excellent": EvaluationRating.excellent, "Good": EvaluationRating.good,
            "Average": EvaluationRating.average, "Poor": EvaluationRating.poor,
        }
        rating = rating_map.get(state["rating"], EvaluationRating.average)

        evaluation = Evaluation(
            answer_id=state["answer_id"], score=state["score"], rating=rating,
            feedback=state["feedback"], strengths=state["strengths"], improvements=state["improvements"]
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        logger.info(f"Evaluation saved! ID={evaluation.id}")
        return {**state, "error": None}
    except Exception as e:
        db.rollback()
        logger.error(f"[save_evaluation] Error: {e}")
        return {**state, "error": str(e)}


def check_completion(state: EvaluationState, db: Session) -> EvaluationState:
    try:
        session = db.query(InterviewSession).filter(InterviewSession.id == state["session_id"]).first()
        if not session:
            return {**state, "all_answered": False, "error": "Session not found"}

        total = db.query(Question).filter(Question.session_id == session.id).count()
        answered = db.query(Answer).join(Question).filter(Question.session_id == session.id).count()

        return {**state, "all_answered": answered >= total, "answered_count": answered, "total_questions": total}
    except Exception as e:
        logger.error(f"[check_completion] Error: {e}")
        return {**state, "all_answered": False, "error": str(e)}


def generate_report_node(state: EvaluationState, db: Session) -> EvaluationState:
    try:
        session = db.query(InterviewSession).filter(InterviewSession.id == state["session_id"]).first()
        candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first()
        questions = (
            db.query(Question).filter(Question.session_id == state["session_id"])
            .order_by(Question.q_index).all()
        )

        qa_pairs, scores = [], []
        for q in questions:
            answer = db.query(Answer).filter(Answer.question_id == q.id).first()
            if answer and answer.evaluation:
                scores.append(answer.evaluation.score)
                qa_pairs.append({"question": q.q_text, "answer": answer.transcript, "score": answer.evaluation.score})

        avg_score = sum(scores) / len(scores) if scores else 0
        report_data = generate_overall_report(
            name=candidate.name, role=candidate.target_role,
            resume_context=candidate.resume_text[:2000], qa_pairs=qa_pairs,
            avg_score=avg_score, answered=state["answered_count"], total=state["total_questions"]
        )

        existing = db.query(OverallReport).filter(OverallReport.session_id == state["session_id"]).first()
        if existing:
            existing.avg_score = avg_score
            existing.strengths_summary = report_data.get("strengths_summary")
            existing.weaknesses_summary = report_data.get("weaknesses_summary")
            existing.hiring_recommendation = report_data.get("hiring_recommendation")
            existing.overall_feedback = report_data.get("overall_feedback")
        else:
            db.add(OverallReport(
                session_id=state["session_id"], avg_score=avg_score,
                total_questions=state["total_questions"], answered=state["answered_count"],
                strengths_summary=report_data.get("strengths_summary"),
                weaknesses_summary=report_data.get("weaknesses_summary"),
                hiring_recommendation=report_data.get("hiring_recommendation"),
                overall_feedback=report_data.get("overall_feedback")
            ))

        session.status = InterviewStatus.completed
        session.total_score = avg_score
        session.completed_at = datetime.utcnow()
        db.commit()
        logger.info(f"Report saved! Avg score: {avg_score:.1f}/10")
        return {**state, "report_generated": True}
    except Exception as e:
        db.rollback()
        logger.error(f"[generate_report_node] Error: {e}")
        return {**state, "report_generated": False, "error": str(e)}