from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import ollama
from nodes import add_node, path_to_root, node_exists_in_db, convert_branch, Branch


app = FastAPI()


class BranchRequest(BaseModel):
     node_id: str
class Turn(BaseModel):
    content: str
    parent_id: str | None = None


def call_model(messages):
    last = messages[-1]["content"]
    reply = ollama.chat(model="qwen2.5:1.5b", messages=messages)
    return reply["message"]["content"]


@app.post('/chat')
def chat(turn: Turn):
    if turn.parent_id is not None and not node_exists_in_db(turn.parent_id):
        raise HTTPException(status_code=404, detail="parent_id not found")
    curr = add_node(role="user", content=turn.content, parent_id = turn.parent_id)
    messages = path_to_root(curr.id)
    print(f"parent_id={turn.parent_id}, history length={len(messages)}")
    text = call_model(messages)
    assist = add_node(role="assistant", content=text, parent_id = curr.id)
    return {"reply": text, "node_id": assist.id}


@app.post('/branch')
def branch(branchreq: BranchRequest):
    new_node = convert_branch(branchreq.node_id)

    if not isinstance(new_node, str) and new_node.branch_id:
        return {"Status": "Branch created", "id": new_node.branch_id}
        
    return {"Status": "Unable to create a branch"}
    



@app.post('/merge')
def merge(turn1: Turn, turn2: Turn):
    """need to summarize and give context to both turns, and get the similarities and differences.
    need to allow the user to choose what they wanted to do """
    return

@app.post('/visualize')
def visualize(messages):
    """build out a graph that shows the messages overall thing."""
    return