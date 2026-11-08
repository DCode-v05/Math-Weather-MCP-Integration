# Math-Weather-MCP-Integration

**A small reference build showing one LangChain agent talking to two MCP servers at once, one over stdio and one over HTTP.**

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white) ![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langgraph&logoColor=white) ![MCP](https://img.shields.io/badge/MCP-FastMCP-000000?style=flat&logo=anthropic&logoColor=white) ![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=flat&logo=groq&logoColor=white) ![asyncio](https://img.shields.io/badge/asyncio-stdlib-3776AB?style=flat&logo=python&logoColor=white) ![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?style=flat&logo=uv&logoColor=white)

## Overview

This is a reference implementation of the **Model Context Protocol (MCP)** with more than one server in play. The point I wanted to prove to myself: a single agent can hold tools from two MCP servers that speak *different* transports and pick the right one on its own, with no manual switching.

There are two servers here. A **Math server** runs as a local subprocess and talks over **stdio**. A **Weather server** runs as a network service and talks over **streamable HTTP**. The client wires both into one `MultiServerMCPClient`, hands the combined tool set to a Groq-hosted Llama 3.3 70B agent, and lets the model route each query: math goes to the math tool, weather goes to the weather tool.

It's deliberately small (about 1.8 KB of Python across three files). The weather tool returns a canned string rather than calling a real API, so treat this as a working skeleton for multi-server, multi-transport MCP agents and not a finished product. I built it as a learning demo alongside other MCP experiments.

## Key Features

- **Two MCP servers, two transports, one agent.** Math over `stdio`, weather over `streamable-http`, both exposed to the same client.
- **`MultiServerMCPClient` aggregation.** Tools from both servers are collected through `langchain-mcp-adapters` and merged into one tool list the agent can call.
- **LLM-driven tool routing.** A LangChain agent backed by `ChatGroq` (Llama 3.3 70B) reads the natural-language question and decides which tool to call. There is no hardcoded `if/else` dispatch.
- **Auto-spawned subprocess server.** The client launches the math server itself (`command: python`, `args: ["mathserver.py"]`), so you don't start it by hand.
- **`FastMCP` tool definitions.** Both servers use the `FastMCP` helper from the `mcp` SDK. Tools are plain Python functions decorated with `@mcp.tool()`, and their docstrings become the tool descriptions the model sees.
- **Async end to end.** Tool discovery (`await client.get_tools()`) and agent calls (`await agent.ainvoke(...)`) are non-blocking.
- **Two worked examples baked in.** On run it asks a math question (`what's (3 + 5) x 12?`) and a weather question (`what is the weather in California?`) and prints both answers, so you can check the wiring in one go.

## How It Works

The project is three files: a client and two servers. The agent never knows or cares which transport a tool lives behind. That's the whole idea.

### Math server (`mathserver.py`): stdio

A `FastMCP("Math")` instance exposes one tool:

```python
@mcp.tool()
def calculate(expr: str) -> float:
    """Evaluate math expression like '(3+5)*12'."""
    return eval(expr)
```

It runs with `mcp.run(transport="stdio")`, so it talks over standard input/output as a child process. The docstring is what the LLM reads to decide when to call it. Note that it uses Python's built-in `eval` on text the model supplies. That's fine for a trusted local demo, but it's the first thing to replace with a safe parser before this goes anywhere real.

### Weather server (`weather.py`): streamable HTTP

A second `FastMCP("Weather")` instance exposes an async tool:

```python
@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the weather location."""
    return "It's always raining in California"
```

It runs with `mcp.run(transport="streamable-http")` and is meant to be reachable at `http://localhost:8000/mcp`. The return value is a fixed string standing in for a real weather API call, which keeps the demo deterministic and free of extra dependencies.

### Client (`client.py`): the agent

The client is where the two transports meet:

```python
client = MultiServerMCPClient({
    "math":    {"command": "python", "args": ["mathserver.py"], "transport": "stdio"},
    "weather": {"url": "http://localhost:8000/mcp", "transport": "streamable_http"},
})
```

From there the flow is:

1. **Discover tools:** `tools = await client.get_tools()` connects to both servers (spawning the math subprocess, opening the HTTP session) and returns their tools as LangChain-compatible tools.
2. **Build the agent:** `model = ChatGroq(model="llama-3.3-70b-versatile")` and `agent = create_agent(model, tools)`. The Groq API key is read from the environment via `python-dotenv`.
3. **Invoke:** each user message goes to `agent.ainvoke({"messages": [...]})`. The model looks at the available tools, calls the relevant one, and folds the result into its answer.
4. **Print:** the final message content for the math and weather questions is printed to the console.

The agent routes purely from the tools' names and docstrings: a math question lands on `calculate`, a weather question lands on `get_weather`.

## Tech Stack

- **Language:** Python 3.13
- **Agent framework:** LangChain (`create_agent`), LangGraph
- **MCP:** `mcp` SDK / `FastMCP`, `langchain-mcp-adapters` (`MultiServerMCPClient`)
- **LLM:** Groq, via `langchain-groq` `ChatGroq`, model `llama-3.3-70b-versatile`
- **Transports:** stdio (subprocess) and streamable HTTP
- **Runtime / tooling:** `asyncio`, `python-dotenv`, `uv` (with `uv.lock` checked in) or plain `pip`

## Getting Started

### Prerequisites

- Python 3.13 (pinned in `.python-version`)
- A **Groq API key** (the free tier works), from the Groq console
- `uv` is optional; `pip` is fine

### Installation

```bash
git clone https://github.com/DCode-v05/Math-Weather-MCP-Integration.git
cd Math-Weather-MCP-Integration

# with uv (uses the checked-in uv.lock)
uv sync

# or with pip
pip install -r requirements.txt
```

`client.py` imports `python-dotenv`, but neither `pyproject.toml` nor `requirements.txt` lists it. If the import fails, run `pip install python-dotenv`.

### Configure

Create a `.env` file in the project root (it's already in `.gitignore`):

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Running

The weather server runs over HTTP, so start it first in its own terminal:

```bash
python weather.py        # serves MCP at http://localhost:8000/mcp
```

Then run the client in a second terminal:

```bash
python client.py
```

You don't need to start the math server yourself, since `client.py` spawns `mathserver.py` as a subprocess over stdio.

The output is two lines, one per built-in question. The wording after each label comes from the model, so it can differ from run to run:

```
Math response: ...
Weather response: ...
```

## Usage

The two questions are hardcoded in `main()` inside `client.py`. To try your own, edit the `content` of the messages passed to `agent.ainvoke`, for example:

```python
resp = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what is 144 / 12 + 7?"}]}
)
print(resp["messages"][-1].content)
```

Anything math-shaped routes to the `calculate` tool; anything weather-shaped routes to `get_weather`. To make the weather answer real, swap the placeholder return in `weather.py` for an actual API call (e.g. Open-Meteo or OpenWeather) keyed on `location`.

## Project Structure

```
Math-Weather-MCP-Integration/
├── client.py          # Agent + MultiServerMCPClient; wires math (stdio) + weather (http), routes via Groq Llama 3.3
├── mathserver.py      # FastMCP "Math" server, calculate() tool, stdio transport
├── weather.py         # FastMCP "Weather" server, get_weather() tool, streamable-http transport
├── pyproject.toml     # Project metadata + dependencies (langchain, langchain-groq, langgraph, mcp, adapters)
├── requirements.txt   # pip dependency list
├── uv.lock            # Locked dependency versions for uv
├── .python-version    # Pins Python 3.13
├── .gitignore         # Ignores .env, caches, virtualenvs and editor files
└── README.md
```

---

## Contact

<table>
  <tr><td><b>Portfolio:</b> <a href="https://www.denistan.me">Denistan</a></td><td><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/denistanb">denistanb</a></td></tr>
  <tr><td><b>GitHub:</b> <a href="https://github.com/DCode-v05">DCode-v05</a></td><td><b>LeetCode:</b> <a href="https://leetcode.com/u/Denistan_B">Denistan_B</a></td></tr>
  <tr><td colspan="2" align="center"><b>Email:</b> <a href="mailto:denistanb05@gmail.com">denistanb05@gmail.com</a></td></tr>
</table>

Made with ❤️ by **Denistan B**
