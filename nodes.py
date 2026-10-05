import uuid
import ollama
from pydantic import BaseModel, ConfigDict
node_collection = {}

class Branch(BaseModel):
    recent_summary: str
    rolling_summary: str

class MergeRequest(BaseModel):
    id: str


class Node(BaseModel):
    model_config = ConfigDict(frozen=False)
    id: str
    parent_id: str | None
    role: str
    content: str
    branch_id: str | None = None
    summary: Branch | None = None



def model_summary(message):
    reply = ollama.chat(model="qwen2.5:1.5b", messages=message)
    return reply["message"]["content"]

def add_node(parent_id, role, content):
    node_id = str(uuid.uuid4())[:8]
    new_node = Node(id=node_id, parent_id=parent_id, role=role, content=content)
    node_collection[node_id] = new_node
    return new_node

def node_exists_in_db(node_id: str):
    return node_collection.get(node_id) is not None

def convert_branch(node_id: str):
    if not node_exists_in_db(node_id):
        return "Node not defined"
    node = node_collection[node_id]
    if node.branch_id is not None:
        return "Branch already defined"

    node.branch_id = str(uuid.uuid4())[:8]

    path = path_to_closest_branch(node_id)
    recent_messages = [{"role": m["role"], "content": m["content"]} for m in path]

    recent_prompt = [{"role": "user", "content": (
        "Summarize the following conversation in bullet points, "
        "keeping only the most important points:\n\n"
        + "\n".join(f'{m["role"]}: {m["content"]}' for m in recent_messages)
    )}]
    recent = model_summary(recent_prompt)

    branch_node = node_collection[path[-1]["id"]]
    prev_rolling = branch_node.summary.rolling_summary if branch_node.summary else ""

    if prev_rolling:
        rolling_prompt = [{"role": "user", "content": (
            "You have a running summary of a conversation so far:\n"
            + prev_rolling
            + "\n\nNew developments to merge in:\n"
            + recent
            + "\n\nCombine them into a single concise bullet-point summary, "
            "treating the running summary as more important."
        )}]
        rolling = model_summary(rolling_prompt)
    else:
        rolling = recent

    node.summary = Branch(recent_summary=recent, rolling_summary=rolling)
    return node


def path_to_root(node_id: str):
    path = []
    while node_id is not None:
        node = node_collection[node_id]
        path.append({"role": node.role, "content": node.content})
        node_id = node.parent_id
    return list(reversed(path))


def path_to_closest_branch(node_id: str):
    path = []
    while node_id is not None:
        node = node_collection[node_id]
        path.append({"role": node.role, "content": node.content, "id": node.id})
        if node_collection[node_id].branch_id is not None:
                    break
        node_id = node.parent_id
    return list(reversed(path))