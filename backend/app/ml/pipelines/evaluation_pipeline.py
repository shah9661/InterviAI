import logging
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from backend.app.ml.pipelines.evaluation_state import EvaluationState
from backend.app.ml.pipelines.evaluation_node import (
    fetch_context, evaluate_answer_node, save_evaluation,
    check_completion, generate_report_node
)
from backend.app.core.logging import get_logger

logger = get_logger("evaluation_pipeline", log_file="logs/evaluation_pipeline.log", level=logging.INFO)


def should_generate_report(state: EvaluationState) -> str:
    return "generate_report" if state.get("all_answered") else END


def build_evaluation_graph(db: Session):
    def _fetch_context(state):    return fetch_context(state, db)
    def _evaluate_answer(state):  return evaluate_answer_node(state, db)
    def _save_evaluation(state):  return save_evaluation(state, db)
    def _check_completion(state): return check_completion(state, db)
    def _generate_report(state):  return generate_report_node(state, db)

    graph = StateGraph(EvaluationState)
    graph.add_node("fetch_context", _fetch_context)
    graph.add_node("evaluate_answer", _evaluate_answer)
    graph.add_node("save_evaluation", _save_evaluation)
    graph.add_node("check_completion", _check_completion)
    graph.add_node("generate_report", _generate_report)

    graph.set_entry_point("fetch_context")
    graph.add_edge("fetch_context", "evaluate_answer")
    graph.add_edge("evaluate_answer", "save_evaluation")
    graph.add_edge("save_evaluation", "check_completion")
    graph.add_conditional_edges(
        "check_completion", should_generate_report,
        {"generate_report": "generate_report", END: END}
    )
    graph.add_edge("generate_report", END)

    return graph.compile()


def run_evaluation_pipeline(db: Session, session_id: int, question_id: int, answer_id: int, transcript: str) -> dict:
    logger.info(f"Starting evaluation pipeline — session={session_id}, question={question_id}, answer={answer_id}")

    initial_state: EvaluationState = {
        "session_id": session_id, "question_id": question_id, "answer_id": answer_id, "transcript": transcript,
        "candidate_name": "", "candidate_role": "", "question_text": "", "resume_context": "",
        "score": None, "rating": None, "feedback": None, "strengths": None, "improvements": None,
        "all_answered": False, "answered_count": 0, "total_questions": 0,
        "report_generated": False, "error": None
    }

    graph = build_evaluation_graph(db)
    result = graph.invoke(initial_state)
    logger.info(f"Pipeline complete! Score: {result.get('score')}/10")
    return result