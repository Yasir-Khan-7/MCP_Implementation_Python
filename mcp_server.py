# server.py
from mcp.server.fastmcp import FastMCP
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create an MCP server
mcp = FastMCP("Todoist Demo")

# Get API keys from environment variables
TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate API keys
if not TODOIST_API_KEY:
    raise ValueError("TODOIST_API_KEY not found in environment variables")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

# Add a unified Todoist tool
@mcp.tool()
def todoist_assistant(prompt: str) -> str:
    """
    All-in-one Todoist assistant that can create tasks or fetch task lists based on natural language prompts
    
    Args:
        prompt: Natural language prompt describing what to do (create task or list tasks)
    
    Returns:
        Response from the Todoist action
    """
    try:
        # Use LLM to understand the intent and extract parameters
        intent, params = determine_todoist_intent(prompt)
        
        if intent == "create_task":
            return create_task(params.get("content"), params.get("due_string", "today"), params.get("priority", 1))
        elif intent == "list_tasks":
            return get_tasks(params.get("filter", ""))
        else:
            return f"Sorry, I couldn't determine what you wanted to do with Todoist. Please try rephrasing your request."
            
    except Exception as e:
        return f"Error processing your Todoist request: {str(e)}"

def determine_todoist_intent(prompt: str):
    """Use LLM to understand the user's intent and extract parameters for Todoist actions"""
    try:
        # Call Groq API to determine intent
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen-2.5-32b",
                "messages": [
                    {"role": "system", "content": """You are an assistant that analyzes Todoist-related requests. 
                    Your job is to determine whether the user wants to:
                    1. Create a new task ("create_task")
                    2. List/view their tasks ("list_tasks")

                    For "create_task", extract:
                    - content: The task description/content (required)
                    - due_string: When the task is due (optional, default "today")
                    - priority: Task priority from 1-4, where 4 is highest (optional, default 1)

                    For "list_tasks", extract:
                    - filter: Any filtering criteria mentioned (optional, default "")

                    Respond in this JSON format ONLY:
                    {"intent": "create_task|list_tasks", "params": {"param1": "value1", ...}}

                    Examples:
                    "Add milk to my shopping list due tomorrow" → {"intent": "create_task", "params": {"content": "Buy milk", "due_string": "tomorrow"}}
                    "Show me my tasks for today" → {"intent": "list_tasks", "params": {"filter": "today"}}
                    "Create high priority task finish report by Friday" → {"intent": "create_task", "params": {"content": "Finish report", "due_string": "Friday", "priority": 4}}"""},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 200
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            try:
                # Parse the LLM response as JSON
                parsed_response = json.loads(llm_response)
                intent = parsed_response.get("intent", "")
                params = parsed_response.get("params", {})
                
                return intent, params
                
            except json.JSONDecodeError:
                print(f"Error parsing LLM response: {llm_response}")
                return "unknown", {}
        else:
            print(f"Error from LLM API: {response.status_code}")
            return "unknown", {}
            
    except Exception as e:
        print(f"Error determining intent: {str(e)}")
        return "unknown", {}

def create_task(content: str, due_string: str = "today", priority: int = 1) -> str:
    """Create a new task in Todoist"""
    try:
        if not content:
            return "Error: No task content provided."
            
        # API endpoint for creating tasks
        url = "https://api.todoist.com/rest/v2/tasks"
        
        # Prepare the payload
        payload = {
            "content": content,
            "due_string": due_string,
            "priority": priority
        }
        
        # Make the API request
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {TODOIST_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        if response.status_code == 200:
            task_data = response.json()
            return f"Task created successfully!\nContent: {task_data['content']}\nDue: {task_data.get('due', {}).get('string', 'Not specified')}\nURL: {task_data.get('url', 'N/A')}"
        else:
            return f"Error creating task: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error creating task: {str(e)}"

def get_tasks(filter: str = "") -> str:
    """Get tasks from Todoist based on the filter"""
    try:
        # Base URL for fetching tasks
        url = "https://api.todoist.com/rest/v2/tasks"
        
        # Add filter if provided
        params = {}
        if filter and filter != "all":
            params["filter"] = filter
            
        # Make the API request
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {TODOIST_API_KEY}"
            },
            params=params
        )
        
        if response.status_code != 200:
            return f"Error fetching Todoist tasks: {response.status_code} - {response.text}"
            
        # Parse the response
        tasks = response.json()
        
        if not tasks:
            return f"No tasks found matching filter: '{filter or 'all'}'"
            
        # Format the tasks for display
        formatted_tasks = []
        for i, task in enumerate(tasks, 1):
            due_info = "No due date"
            if task.get("due"):
                due_info = task["due"].get("string", "Not specified")
                
            priority = task.get("priority", 1)
            priority_text = "★" * priority
            
            formatted_tasks.append(f"{i}. {task['content']}")
            formatted_tasks.append(f"   Due: {due_info}")
            formatted_tasks.append(f"   Priority: {priority_text}")
            project_id = task.get("project_id")
            if project_id:
                formatted_tasks.append(f"   Project ID: {project_id}")
            formatted_tasks.append("")
            
        result = "\n".join(formatted_tasks)
        return f"Todoist tasks for filter '{filter or 'all'}':\n\n{result}"
            
    except Exception as e:
        return f"Error fetching Todoist tasks: {str(e)}"


# Start the server if this file is run directly
if __name__ == "__main__":
    # Print server info
    print("Starting Todoist MCP Server...")
    
    # Print available tools
    print("Available tools:")
    print("- todoist_assistant")
    
    # Run the server with SSE transport
    mcp.run(transport="sse")