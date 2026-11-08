# Math-Weather-MCP-Integration

A LangChain agent that uses tools from two MCP servers at once, one over stdio and one over streamable HTTP. I wrote it to check that a single agent can hold tools from servers with different transports and pick the right one by itself.

It is deliberately small: three Python files. The weather tool returns a fixed string instead of calling a weather API, so treat it as a skeleton.

## How it works

- `mathserver.py` is a `FastMCP("Math")` server with one tool, `calculate(expr)`, which runs Python's `eval` on the expression. Fine for a local demo, not for anything exposed. It runs over stdio.
- `weather.py` is a `FastMCP("Weather")` server with one async tool, `get_weather(location)`, which always returns `"It's always raining in California"`. It runs over streamable HTTP, at `http://localhost:8000/mcp`.
- `client.py` builds a `MultiServerMCPClient` with both servers (it starts `mathserver.py` itself as a subprocess), loads their tools, and passes them to a `create_agent` agent using `ChatGroq` with `llama-3.3-70b-versatile`. It then asks two hardcoded questions, "what's (3 + 5) x 12?" and "what is the weather in California?", and prints the answers.

The model chooses between `calculate` and `get_weather` from the tool names and docstrings. There is no routing code.

## Stack

Python 3.13, LangChain, LangGraph, `langchain-mcp-adapters`, `mcp` (FastMCP), `langchain-groq`, `python-dotenv`.

## Setup

You need Python 3.13 (see `.python-version`) and a Groq API key.

```bash
uv sync
```

or `pip install -r requirements.txt`.

Create `.env`:

```
GROQ_API_KEY=your_key
```

Start the weather server in one terminal:

```bash
python weather.py
```

Run the client in another:

```bash
python client.py
```

It prints one line for the math answer and one for the weather answer. To try other questions, change the message content in `main()` in `client.py`.

## Structure

```
client.py       agent and MultiServerMCPClient
mathserver.py   Math MCP server (stdio)
weather.py      Weather MCP server (streamable HTTP)
pyproject.toml, requirements.txt, uv.lock, .python-version
```
