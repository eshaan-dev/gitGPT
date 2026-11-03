from mcp.server.mcpserver import MCPServer
import ollama
from nodes import add_node, path_summary_collection, node_exists_in_db, convert_branch

mcp = MCPServer("gitGPT")


def call_model(messages):
    reply = ollama.chat(model="qwen2.5:1.5b", messages=messages)
    return reply["message"]["content"]


@mcp.tool()
def chat(content: str, parent_id: str | None = None) -> dict:
    """Send a message and get a reply. Returns reply and node_id.
    Pass the returned node_id as parent_id on the next call to continue the conversation."""
    if parent_id is not None and not node_exists_in_db(parent_id):
        return {"error": f"parent_id '{parent_id}' not found"}
    curr = add_node(role="user", content=content, parent_id=parent_id)
    messages = path_summary_collection(curr.id)
    text = call_model(messages)
    assist = add_node(role="assistant", content=text, parent_id=curr.id)
    return {"reply": text, "node_id": assist.id}


@mcp.tool()
def branch(node_id: str) -> dict:
    """Mark a node as a branch point, computing a summary of the conversation up to that point.
    Use this before diverging the conversation in a new direction."""
    result = convert_branch(node_id)
    if isinstance(result, str):
        return {"error": result}
    return {"status": "Branch created", "branch_id": result.branch_id}


@mcp.tool()
def rollback(node_id: str) -> dict:
    """Roll back to a previous message node. Returns the node_id to use as parent_id
    in the next chat call to resume the conversation from that point."""
    if not node_exists_in_db(node_id):
        return {"error": f"node_id '{node_id}' not found"}
    return {"status": "Ready to resume from this node", "node_id": node_id}


if __name__ == "__main__":
    mcp.run()
