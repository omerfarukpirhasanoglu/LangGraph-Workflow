from langgraph.graph import StateGraph, START, END
from state import ChromaState
from nodes import (
    run_model, load_history, contextual_interpret, route_after_interpretation,
    ask_user, self_criticism, update_history,
)

def build_graph(checkpointer):
    builder = StateGraph(ChromaState)
    builder.add_node("run_model", run_model)
    builder.add_node("load_history", load_history)
    builder.add_node("contextual_interpret", contextual_interpret)
    builder.add_node("ask_user", ask_user)
    builder.add_node("self_criticism", self_criticism)
    builder.add_node("update_history", update_history)

    builder.add_edge(START, "run_model")
    builder.add_edge("run_model", "load_history")
    builder.add_edge("load_history", "contextual_interpret")
    builder.add_conditional_edges(
        "contextual_interpret",
        route_after_interpretation,
        {"ask_user": "ask_user", "self_criticism": "self_criticism"},
    )
    builder.add_edge("ask_user", "contextual_interpret")
    builder.add_edge("self_criticism", "update_history")
    builder.add_edge("update_history", END)

    return builder.compile(checkpointer=checkpointer)