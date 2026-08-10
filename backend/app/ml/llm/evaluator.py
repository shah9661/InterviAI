import logging
from typing import List
from langchain_core.output_parsers import JsonOutputParser

from backend.app.ml.llm.client import get_llm
from backend.app.ml.llm.prompts import EVALUATION_PROMPT, OVERALL_REPORT_PROMPT
from backend.app.core.logging import get_logger

logger = get_logger("evaluator", log_file="logs/evaluator.log", level=logging.INFO)


def get_evaluation_chain():
    llm = get_llm(temperature=0.2)
    parser = JsonOutputParser()
    return EVALUATION_PROMPT | llm | parser


def get_report_chain():
    llm = get_llm(temperature=0.3)
    parser = JsonOutputParser()
    return OVERALL_REPORT_PROMPT | llm | parser


def evaluate_answer(
    name: str,
    role: str,
    resume_context: str,
    question: str,
    answer: str
) -> dict:
    try:
        chain = get_evaluation_chain()
        result = chain.invoke({
            "name": name,
            "role": role,
            "resume_context": resume_context,
            "question": question,
            "answer": answer
        })
    except Exception as e:
        logger.error(f"Answer evaluation failed for {name}: {e}")
        raise

    score = int(result.get("score", 0))
    result["score"] = max(0, min(10, score))

    valid_ratings = {"Excellent", "Good", "Average", "Poor"}
    if result.get("rating") not in valid_ratings:
        result["rating"] = "Average"

    logger.info(f"Evaluated answer for {name} — score: {result['score']}/10")
    return result


def generate_overall_report(
    name: str,
    role: str,
    resume_context: str,
    qa_pairs: List[dict],
    avg_score: float,
    answered: int,
    total: int
) -> dict:
    qa_summary = "\n\n".join([
        f"Q{i+1} [{pair['score']}/10]: {pair['question']}\n"
        f"Answer: {pair['answer'][:300]}{'...' if len(pair['answer']) > 300 else ''}"
        for i, pair in enumerate(qa_pairs)
    ])

    try:
        chain = get_report_chain()
        result = chain.invoke({
            "name": name,
            "role": role,
            "resume_context": resume_context[:2000],
            "qa_summary": qa_summary,
            "avg_score": round(avg_score, 1),
            "answered": answered,
            "total": total
        })
    except Exception as e:
        logger.error(f"Overall report generation failed for {name}: {e}")
        raise

    logger.info(f"Overall report generated for {name} — avg score {avg_score:.1f}/10")
    return result