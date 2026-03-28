import json
import os
import uuid
from typing import Any

from fastapi import FastAPI, Request
from openai import OpenAI
from fastapi.responses import StreamingResponse

# Defaults can be overridden by AGENT_HUB_REGION.
REGION = "us-chicago-1"
MODEL_ID = "openai.gpt-oss-120b"

BASE_URL = f"https://inference.generativeai.{REGION}.oci.oraclecloud.com/20231130/openai/v1"
PROJECT_OCID = os.environ.get("TF_VAR_project_ocid")
GENAI_API_KEY = os.environ.get("TF_VAR_genai_api_key")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL")

client = OpenAI(
    base_url=BASE_URL,
    api_key=GENAI_API_KEY,
    project=PROJECT_OCID,
)

app = FastAPI()


def log(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def get_tools() -> list[dict[str, Any]]:
    if not MCP_SERVER_URL:
        return []
    return [
        {
            "type": "mcp",
            "server_label": "mcp",
            "server_url": MCP_SERVER_URL,
            "require_approval": "never",
        }
    ]

# Simple in-memory state for demo compatibility with chat.js protocol.
THREADS: dict[str, dict[str, Any]] = {}

@app.get("/chat")
def chat(q: str):
    response = client.responses.create(
        model=MODEL_ID,
        temperature=0.0,
        tools=get_tools(),
        input=q,
    )
    return response.output_text


@app.post("/threads")
@app.post("/app/threads")
def create_thread() -> dict[str, str]:
    thread_id = str(uuid.uuid4())
    THREADS[thread_id] = {"next_message_id": 1}
    return {"thread_id": thread_id}


@app.post("/assistants/search")
@app.post("/app/assistants/search")
def assistants_search() -> list[dict[str, str]]:
    # chat.js expects an array of objects with a graph_id field.
    return [{"graph_id": "agent"}]


@app.post("/threads/{thread_id}/runs/stream")
@app.post("/app/threads/{thread_id}/runs/stream")
def runs_stream(thread_id: str, payload: dict[str, Any], request: Request):
    if thread_id not in THREADS:
        THREADS[thread_id] = {"next_message_id": 1}

    messages = payload.get("input", {}).get("messages", [])
    log("<runs_stream> messages=", messages)
    question = ""
    if messages:
        question = messages[-1].get("content", "")
    log("<runs_stream> question=", question)

    authorization = request.headers.get("authorization")
    response_kwargs: dict[str, Any] = {
        "model": MODEL_ID,
        "temperature": 0.0,
        "tools": get_tools(),
        "input": question,
    }
    if authorization and authorization.lower().startswith("bearer "):
        response_kwargs["extra_headers"] = {"Authorization": authorization}
        log("<runs_stream> forwarding bearer authorization header")

    def event_stream():
        log("<event_stream> question=", question)
        response = client.responses.create(**response_kwargs)
        log("<event_stream> output_text=", response.output_text)
        log("<event_stream> response=", response)

        message_id = int(THREADS[thread_id].get("next_message_id", 1))
        THREADS[thread_id]["next_message_id"] = message_id + 1

        event = {
            "messages": {
                str(message_id): {
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
