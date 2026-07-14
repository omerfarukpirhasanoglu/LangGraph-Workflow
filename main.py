import os
import tempfile
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langgraph.types import Command
from checkpointer import get_checkpointer
from graph import build_graph

ALLOWED_TYPES = {".jpg", ".jpeg", ".png", ".webp"}

graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph
    with get_checkpointer() as checkpointer:
        graph = build_graph(checkpointer)
        yield


app = FastAPI(title="Chroma Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_ORIGIN")],
    allow_methods=["POST"],
    allow_headers=["*"],
)


def _format_response(state: dict, thread_id: str) -> dict:

    model_output = state.get("model_output", {})
    response = {**model_output, "thread_id": thread_id}

    if "__interrupt__" in state:
        response["agent_status"] = "needs_clarification"
        response["question"] = state["__interrupt__"][0].value["question"]
    else:
        response["agent_status"] = "completed"
        response["final_response"] = state.get("final_response")

    return response


@app.post("/analyze")
async def analyze(file: UploadFile = File(...), device_id: str = Form(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen dosya türü: {ext}")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = graph.invoke({"image_ref": tmp_path, "device_id": device_id}, config)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    finally:
        os.remove(tmp_path)

    return _format_response(result, thread_id)


class ResumeRequest(BaseModel):
    thread_id: str
    answer: str


@app.post("/analyze/resume")
async def resume(payload: ResumeRequest):
    config = {"configurable": {"thread_id": payload.thread_id}}

    try:
        result = graph.invoke(Command(resume=payload.answer), config)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return _format_response(result, payload.thread_id)
