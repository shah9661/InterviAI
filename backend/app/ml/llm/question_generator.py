import logging
from typing import List
from langchain_core.output_parsers import JsonOutputParser

from backend.app.schemas.interview import InterviewQuestionsOutput
from backend.app.ml.llm.client import get_llm
from backend.app.ml.llm.prompts import QUESTION_GENERATION_PROMPT
from backend.app.core.logging import get_logger

logger = get_logger("question_generator", log_file="logs/question_generator.log", level=logging.INFO)


def get_question_generation_chain():
    llm = get_llm(temperature=0.8)
    parser = JsonOutputParser(pydantic_object=InterviewQuestionsOutput)
    return QUESTION_GENERATION_PROMPT | llm | parser


def generate_questions(
    name: str,
    role: str,
    resume_context: str,
    num_questions: int = 5
) -> List[dict]:
    try:
        chain = get_question_generation_chain()
        result = chain.invoke({
            "name": name,
            "role": role,
            "resume_context": resume_context,
            "num_questions": num_questions
        })
    except Exception as e:
        logger.error(f"Question generation failed for {name}: {e}")
        raise

    questions = result.get("questions", [])
    valid_types = {"technical", "behavioral", "situational"}
    for q in questions:
        if q.get("q_type") not in valid_types:
            q["q_type"] = "technical"

    logger.info(f"Generated {len(questions)} questions for {name} ({role})")
    return questions[:num_questions]