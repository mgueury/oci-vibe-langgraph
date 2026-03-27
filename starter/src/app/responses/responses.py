import json
import os
import uuid
from typing import Any

from fastapi import FastAPI
from openai import OpenAI
from fastapi.responses import StreamingResponse

# Defaults can be overridden by AGENT_HUB_REGION.
REGION = "us-chicago-1"
MODEL_ID = "openai.gpt-oss-120b"

BASE_URL = f"https://inference.generativeai.{REGION}.oci.oraclecloud.com/20231130/openai/v1"
PROJECT_OCID = os.environ.get("TF_VAR_project_ocid")
GENAI_API_KEY = os.environ.get("TF_VAR_genai_api_key")

client = OpenAI(
    base_url=BASE_URL,
    api_key=GENAI_API_KEY,
    project=PROJECT_OCID,
)

app = FastAPI()

# Simple in-memory state for demo compatibility with chat.js protocol.
THREADS: dict[str, dict[str, Any]] = {}

@app.get("/chat")
def chat(q: str):
    response = client.responses.create(
        model=MODEL_ID,
        temperature=0.0,
        input=q,
    )
    return response.output_text


@app.post("/threads")
@app.post("/app/threads")
def create_thread() -> dict[str, str]:
    thread_id = str(uuid.uuid4())
    THREADS[thread_id] = {}
    return {"thread_id": thread_id}


@app.post("/assistants/search")
@app.post("/app/assistants/search")
def assistants_search() -> list[dict[str, str]]:
    # chat.js expects an array of objects with a graph_id field.
    return [{"graph_id": "agent"}]


@app.post("/threads/{thread_id}/runs/stream")
@app.post("/app/threads/{thread_id}/runs/stream")
def runs_stream(thread_id: str, payload: dict[str, Any]):
    messages = payload.get("input", {}).get("messages", [])
    question = ""
    if messages:
        question = messages[-1].get("content", "")

    def event_stream():
        response = client.responses.create(
            model=MODEL_ID,
            temperature=0.0,
            input=question,
        )
        event = {
            "messages": {
                "1": {
                    "type": "ai",
                    "content": response.output_text,
                }
            }
        }
        # chat.js splits on CRLF + CRLF and expects lines starting with "data:"
        yield f"data: {json.dumps(event)}\r\n\r\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
