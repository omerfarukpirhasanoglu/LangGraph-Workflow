from langgraph.types import interrupt
from config import get_llm
from tools import call_chroma_model
from prompts import (
    InterpretationResult,
    INTERPRETATION_SYSTEM_PROMPT,
    format_interpretation_input,
    CritiqueResult,
    SELF_CRITICISM_SYSTEM_PROMPT,
    format_critique_input,
)
from state import ChromaState

from history import build_summary_line, add_history_entry, get_history_summary


def run_model(state: ChromaState) -> dict:

    output = call_chroma_model(state["image_ref"])
    return {"model_output": output}

def load_history(state: ChromaState) -> dict:

    summary = get_history_summary(state["device_id"])
    return {"history_summary": summary}

def contextual_interpret(state: ChromaState) -> dict:

    llm = get_llm("reasoning").with_structured_output(InterpretationResult)
    user_input = format_interpretation_input(
        model_output=state["model_output"],
        history_summary=state.get("history_summary", ""),
        user_context=state.get("user_context"),
    )
    result: InterpretationResult = llm.invoke([
        ("system", INTERPRETATION_SYSTEM_PROMPT),
        ("human", user_input),
    ])

    # ikinci soru olamaz
    already_asked = state.get("clarification_asked", False)
    needs_clarification = result.needs_clarification and not already_asked

    return {
        "needs_clarification": needs_clarification,
        "interpretation": result.interpretation,
        "_clarifying_question": result.clarifying_question,
    }


def route_after_interpretation(state: ChromaState) -> str:

    return "ask_user" if state.get("needs_clarification") else "self_criticism"


def ask_user(state: ChromaState) -> dict:

    question = state.get("_clarifying_question") or "Bu kombini ne için giyeceksiniz?"
    answer = interrupt({"question": question})
    return {"user_context": answer, "clarification_asked": True}


def self_criticism(state: ChromaState) -> dict:

    llm = get_llm("reasoning").with_structured_output(CritiqueResult)
    user_input = format_critique_input(
        interpretation=state["interpretation"],
        model_output=state["model_output"],
    )
    result: CritiqueResult = llm.invoke([
        ("system", SELF_CRITICISM_SYSTEM_PROMPT),
        ("human", user_input),
    ])
    return {"final_response": result.final_response}


def update_history(state: ChromaState) -> dict:

    line = build_summary_line(state["model_output"], state.get("user_context"))
    add_history_entry(state["device_id"], line)
    return {}