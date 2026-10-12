# gitGPT

Version control for LLM conversations. gitGPT stores a chat as a **tree of messages** instead of a flat list. You can roll back to any earlier message with preserved history, and branch off from it the same way you would with commits in git.

The model behind this project runs locally through (`qwen2.5:1.5b` by default) via Ollama, and the backend is a small [FastAPI] server. You can replace this model with an API call within main.py with the call_model function. 

## How it works

- **Every message is a node.** Each user and assistant message gets a short ID and a pointer to its parent. Following parent pointers from any node gives you that conversation's history.
- **Rollback.** Continue a conversation from any earlier node by sending its ID as the parent of your next message. The old path is still there; you've just started a new one.
- **Branches with summaries.** Marking a node as a branch asks the model to summarize the conversation since the previous branch point (a *recent summary*) and merge it into a running *rolling summary*. Later messages on that branch get the rolling summary as context instead of the full history.
- **Automatic context compression.** The model only sees the last ~10 messages. When a path gets 10 messages deep, gitGPT inserts a `system` summary node so older context survives in condensed form.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/download), running locally

## Setup

```bash
git clone https://github.com/eshaan-dev/gitGPT.git
cd gitGPT

# Install dependencies
uv sync

# Download the model
ollama pull qwen2.5:1.5b
```

Make sure Ollama is running (`ollama serve`, or open the Ollama app).

## Running

**1. Start the API server**

```bash
uv run fastapi dev main.py
```

The server starts at `http://localhost:8000`. Interactive API docs are at `http://localhost:8000/docs`.

**2. Start the terminal client** (in a second terminal)

```bash
uv run --with requests python parse.py
```

The client uses `requests`, which isn't in the project dependencies yet, so `--with requests` pulls it in for this run.

### Client commands

| Input | What it does |
|---|---|
| any text | Sends a message and continues from the current node |
| `/rollback <node_id>` | Moves back to an earlier node; your next message continues from there |
| `/branch` | Marks the current node as a branch point and summarizes the conversation up to it |
| `exit` | Quits the client |

Each assistant reply is printed with its node ID, which is what you pass to `/rollback`.

**Example**

```
You: What's a good first project for learning Rust?
Assistant: ... id: 3f9a1c2e
You: How about something with networking?
Assistant: ... id: 8b20d7f1
You: /rollback 3f9a1c2e
Rollback Successful!
You: What about something with graphics instead?
Assistant: ... id: c41e9a07
```

The networking path and the graphics path now both exist, branching from `3f9a1c2e`.

## API

### `POST /chat`

Adds a user message, gets a reply from the model, and stores both.

```json
// request
{ "content": "Hello!", "parent_id": null }

// response
{ "reply": "Hi! How can I help?", "node_id": "a1b2c3d4" }
```

Pass `parent_id: null` to start a new conversation. An unknown `parent_id` returns `404`.

### `POST /branch`

Turns a node into a branch point and generates its summaries.

```json
// request
{ "node_id": "a1b2c3d4" }

// response
{ "Status": "Branch created", "id": "e5f6a7b8" }
```

Returns `{"Status": "Unable to create a branch"}` if the node doesn't exist or is already a branch.

### Planned

- `POST /merge`: combine two branches by summarizing their similarities and differences and letting the user choose how to merge them
- `POST /visualize`: render the conversation tree as a graph

Both endpoints exist as stubs but aren't implemented yet.

## Project structure

```
.
├── main.py            # FastAPI app: /chat, /branch, plus /merge and /visualize stubs
├── nodes.py           # Node model, the in-memory tree, branching and summarization
├── parse.py           # Terminal client for the API
├── src/gitgpt/        # Package entry point (placeholder)
├── pyproject.toml
└── uv.lock
```

## Configuration

The model is hardcoded as `qwen2.5:1.5b` in `call_model` (`main.py`) and `model_summary` (`nodes.py`). To use a different Ollama model, pull it and change both places.

## Limitations

- **In-memory storage.** All conversations live in a Python dict and are lost when the server restarts.
- **Small default model.** `qwen2.5:1.5b` is fast but its summaries can be rough. A larger model will summarize better.
- Merge and visualization aren't built yet.

## License

[MIT](LICENSE)
