# 🧩 Model Context Protocol (MCP) Implementation in Python
This repository offers a Python implementation of the Model Context Protocol (MCP), an open standard that streamlines the integration between large language models (LLMs) and external data sources or tools. MCP functions similarly to a USB-C port for AI applications, providing a standardized interface for connecting AI models to various peripherals and accessories. 



# Todoist MCP Assistant

A simplified Todoist task manager that uses the Model Context Protocol (MCP) to provide a natural language interface for creating and viewing Todoist tasks.

## Setup

1. Install dependencies:
   ```
   pip install mcp python-dotenv requests
   ```

2. Ensure you have a `.env` file in the root directory with your API keys:
   ```
   # Todoist API key
   TODOIST_API_KEY=your_todoist_api_key

   # Groq API key
   GROQ_API_KEY=your_groq_api_key
   ```

## Running the Application

### Option 1: All-in-one Script (Recommended)
```
python run.py
```
This will start both the server and client in a single command.

### Option 2: Manual Startup

#### Start the Server
```
python mcp_server.py
```

#### Start the Client
In a separate terminal window:
```
python mcp_client.py
```

## Usage Examples

The client supports natural language inputs like:
- "Create a task to buy groceries tomorrow"
- "Add high priority task to finish report by Friday"
- "Show me my tasks for today"
- "List all my tasks"

Type 'exit' to quit the client.

## How It Works

1. The server exposes a single MCP tool called `todoist_assistant` that accepts natural language prompts
2. The Groq LLM interprets the user's intent (create task or list tasks)
3. The server calls the appropriate Todoist API based on the interpreted intent
4. Results are returned to the client for display

## Security Note

API keys are stored in the `.env` file and are loaded at runtime. This file is excluded from version control (.gitignore) to prevent accidental exposure of sensitive keys. 