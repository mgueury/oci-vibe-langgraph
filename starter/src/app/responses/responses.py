from openai import OpenAI
import os
from fastapi import FastAPI

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

@app.get("/chat")
def chat(q: str):
    response = client.responses.create(
        model=MODEL_ID,
        temperature=0.0,
        input=q,
    )

    print("Request:", request)
    print(response.output_text)
    print("")
    print("Full response:", response)
    print("")

    return response.output_text

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
