from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Observation(BaseModel):
    text: str
    metadata: dict 
    step_count: int

class Action(BaseModel):
    label: str  
    confidence: float

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict

CASES = {
    "task_1": {"t": "Go back to your country.", "tags": ["hostile"], "rep": 0.1, "ans": "BLOCK"},
    "task_2": {"t": "Xanax 50mg - no prescription - fast shipping", "tags": ["medical"], "rep": 0.2, "ans": "BLOCK"},
    "task_3": {"t": "That's my bitch! Love her.", "tags": ["reclaimed-slang", "lgbtq-plus"], "rep": 0.9, "ans": "ALLOW"}
}

@app.post("/reset", response_model=Observation)
async def reset(task_id: str = "task_1"):
    c = CASES.get(task_id, CASES["task_1"])
    return Observation(text=c["t"], metadata={"tags": c["tags"], "rep": c["rep"]}, step_count=0)

@app.post("/step", response_model=StepResponse)
async def step(action: Action, task_id: str = "task_1"):
    c = CASES.get(task_id, CASES["task_1"])
    
    is_correct = (action.label == c["ans"])
    reward = 1.0 if is_correct else -1.0
    
    if is_correct and action.confidence < 0.6:
        reward -= 0.3
    return StepResponse(
        observation=Observation(text="EOF", metadata={}, step_count=1),
        reward=reward,
        done=True,
        info={"target": c["ans"], "case": task_id}
    )

@app.get("/state")
async def state(): return {"status": "ready"}