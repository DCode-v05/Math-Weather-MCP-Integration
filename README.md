# Math & Weather MCP Integration

## Project Description
This project demonstrates a robust **Multi-Server Model Context Protocol (MCP)** implementation. It features an intelligent agent utilizing **Groq's Llama 3.3** model via **LangChain** to seamlessly interact with two distinct MCP servers simultaneously: a Math server (communicating via standard I/O) and a Weather server (communicating via HTTP). This project serves as a reference implementation for building complex, multi-tool agentic workflows using the MCP standard.

---

## Project Details

### Overview
The core objective is to showcase interoperability between different MCP transport layers within a single client application. The agent dynamically routes user queries to the appropriate server—solving math problems or checking weather conditions—without explicit user switching.

### Key Components
- **Multi-Server Client (`client.py`)**: 
  - Initializes a `MultiServerMCPClient` to bridge multiple tools.
  - Connects to the **Math Server** using `stdio` transport.
  - Connects to the **Weather Server** using `streamable-http` transport.
  - Uses `ChatGroq` (Llama-3.3-70b-versatile) for reasoning and tool invocation.

- **Math Server (`mathserver.py`)**:
  - Built with `FastMCP`.
  - Provides a `calculate` tool to evaluate mathematical expressions.
  - Runs as a subprocess via standard input/output.

- **Weather Server (`weather.py`)**:
  - Built with `FastMCP`.
  - Provides a `get_weather` tool.
  - Configured to run as an HTTP server (`streamable-http`), meant to run on `localhost:8000`.

### Features
- **Hybrid Transport Support**: Demonstrates handling both local process (`stdio`) and network-based (`http`) MCP servers.
- **Dynamic Tool Selection**: The LLM intelligently selects the correct tool based on natural language queries.
- **Asynchronous Execution**: Uses `asyncio` for efficient non-blocking operations.

---

## Tech Stack
- **Language**: Python 3.x
- **Core Frameworks**: 
  - [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
  - [LangChain](https://www.langchain.com/)
  - [LangGraph](https://langchain-ai.github.io/langgraph/)
- **AI Model**: Groq (Llama-3.3-70b-versatile)
- **Utilities**: `python-dotenv`, `uv` (optional for package management)

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/DCode-v05/Math-Weather-MCP-Integration.git
cd Math-Weather-MCP-Integration
```

### 2. Install dependencies
Ensure you have Python installed. It is recommended to use a virtual environment.
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the Application
Since the Weather server operates over HTTP, you may need to start it separately depending on the deployment, but for this demonstration the client connects to `localhost:8000`.

**Step 1: Start the Weather Server** (if running separately)
```bash
python weather.py
```

**Step 2: Run the Client** (in a new terminal)
```bash
python client.py
```
*Note: The `client.py` script is configured to look for the weather server at `http://localhost:8000/mcp` and will spawn the math server automatically.*

---

## Usage
Once the client is running, the agent performs the following autonomous checks:
1. **Math Query**: Automatically asks "what's (3 + 5) x 12?" and prints the result from the Math Server.
2. **Weather Query**: Automatically asks "what is the weather in California?" and prints the result from the Weather Server.

You can modify the `main()` function in `client.py` to send your own custom queries.

---

## Project Structure
```
Math-Weather-MCP-Integration/
│
├── client.py            # Main client application entry point
├── mathserver.py        # MCP server for math operations (stdio)
├── weather.py           # MCP server for weather data (http)
├── .env                 # Environment variables (API Keys)
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request describing your changes.

---

## Contact
- **GitHub:** [DCode-v05](https://github.com/DCode-v05)
- **Email:** denistanb05@gmail.com
