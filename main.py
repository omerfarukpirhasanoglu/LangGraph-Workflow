from langgraph.types import Command
from checkpointer import get_checkpointer
from graph import build_graph
import uuid

def new_thread_id() -> str:
    return str(uuid.uuid4())

with get_checkpointer() as checkpointer:
    graph = build_graph(checkpointer)
    
    config = {"configurable": {"thread_id": new_thread_id()}}

    result = graph.invoke({"image_ref": "kombin.jpg", "device_id": "gelen-device-id"}, config)

    if "__interrupt__" in result:
        question = result["__interrupt__"][0].value["question"]
        print(f"Soru: {question}")
        answer = input("> ")
        result = graph.invoke(Command(resume=answer), config)

    print(result["final_response"])