import uuid

nodes = {}   # id -> node


def add_node(role, content, parent_id):
    node_id = str(uuid.uuid4())[:8]
    nodes[node_id] = {
        "id": node_id,
        "parent_id": parent_id,
        "role": role,
        "content": content,
    }
    return node_id


def path_to_root(node_id):
    path = []
    while node_id is not None:
        node = nodes[node_id]
        path.append({"role": node["role"], "content": node["content"]})
        node_id = node["parent_id"]
    return list(reversed(path))