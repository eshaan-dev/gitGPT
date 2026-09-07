
from fastapi import FastAPI
from pydantic import BaseModel
import ollama
from nodes import add_node, path_to_root, nodes
app = FastAPI()

messages = []

class Turn(BaseModel):
    content: str


def call_model(messages):
    last = messages[-1]["content"]
    reply = ollama.chat(model="qwen3.5:4b", messages=messages)
    return reply["message"]["content"]


@app.post('/chat')
def chat(turn: Turn):
    messages.append({"role": "user", "content": turn.content})
    text = call_model(messages)
    messages.append({"role": "assistant", "content": text})
    return {"reply": text}

    
@app.get("/history")
def history():
    return messages


