from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tracer import run_code

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Dry Run Visualizer API")

# CORS — allow the plain HTML frontend (opened as a local file or any origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class CodeRequest(BaseModel):
    code: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/run")
def execute_code(req: CodeRequest):
    """
    Accept a snippet of Python code, run it under the tracer, and return
    the collected steps.

    Response shape:
        {
            "steps": [
                {"line": 1, "variables": {"x": 1}},
                {"line": 2, "variables": {"x": 1, "y": 2}},
                {"line": 3, "error": "ZeroDivisionError: division by zero"}
            ]
        }
    """
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    try:
        steps = run_code(req.code)
    except Exception as exc:
        # Unexpected tracer-level failure — surface it cleanly
        raise HTTPException(status_code=500, detail=f"Tracer error: {exc}")

    return {"steps": steps}