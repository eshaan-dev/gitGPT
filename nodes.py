import uuid
from pydantic import BaseModel

node_collection = {}

class Node(BaseModel):
    id: str
    parent_id: str | None
    role: str
    content: str

class MergeRequest(BaseModel):
    id: str

def add_node(parent_id, role, content):
    node_id = str(uuid.uuid4())[:8]
    new_node = Node(id=node_id, parent_id=parent_id, role=role, content=content)
    node_collection[node_id] = new_node
    return new_node

def node_exists_in_db(node_id: str):
    return node_collection.get(node_id) is not None
def path_to_root(node_id: str):
    path = []
    while node_id is not None:
        node = node_collection[node_id]
        path.append({"role": node.role, "content": node.content})
        node_id = node.parent_id
    return list(reversed(path))