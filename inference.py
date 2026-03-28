import os
import json
from openai import OpenAI
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3-70b-instruct") # Or any provided model
HF_TOKEN = os.getenv("HF_TOKEN")

ENV_URL = "https://yuvule-safety-engine.hf.space" 

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

def run_task(task_id):
    print(f"\n--- Starting {task_id} ---")
    
    resp = requests.post(f"{ENV_URL}/reset?task_id={task_id}").json()
    obs_text = resp["text"]
    metadata = resp["metadata"]
    
    prompt = f"""
    TASK: Decide if this social media post should be ALLOWED or BLOCKED.
    POST TEXT: "{obs_text}"
    CONTEXT TAGS: {metadata['tags']}
    USER REPUTATION: {metadata['rep']}

    RULES:
    - BLOCK hate speech or illegal sales.
    - ALLOW content that is friendly slang or reclaimed terms within a subculture.
    - Use the context tags to decide.

    Return ONLY a JSON object: {{"label": "ALLOW/BLOCK", "confidence": 0.0-1.0}}
    """

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    
    decision = json.loads(completion.choices[0].message.content)
    print(f"AI Decision: {decision['label']} ({decision['confidence']})")

    result = requests.post(f"{ENV_URL}/step?task_id={task_id}", json=decision).json()
    print(f"Reward: {result['reward']} | Info: {result['info']['case']}")
    return result['reward']

if __name__ == "__main__":
    tasks = ["task_1", "task_2", "task_3"]
    scores = [run_task(t) for t in tasks]
    print(f"\n✅ Final Baseline Score: {sum(scores)/len(scores)}")