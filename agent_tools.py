import requests
import asyncio
from langchain_core.tools import tool
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession


# Mock Tools to call FastAPI
FASTAPI_URL = "http://localhost:8000"

@tool
def unlock_peoplesoft_account(user_id: str) -> str:
    """Unlocks a PeopleSoft account for a given user_id after failed login attempts."""
    try:
        response = requests.post(f"{FASTAPI_URL}/api/peoplesoft/unlock", json={"user_id": user_id})
        if response.status_code == 200:
            return response.json().get("message", f"SUCCESS: unlocked {user_id}")
        return f"FAILED: API returned {response.status_code} - {response.text}"
    except Exception as e:
        return f"FAILED to call API: {str(e)}"

@tool
def reset_peoplesoft_pwd(user_id: str) -> str:
    """Resets the PeopleSoft password to a temporary password for a given user_id."""
    try:
        response = requests.post(f"{FASTAPI_URL}/api/peoplesoft/reset_password", json={"user_id": user_id})
        if response.status_code == 200:
            return response.json().get("message", f"SUCCESS: reset {user_id}")
        return f"FAILED: API returned {response.status_code} - {response.text}"
    except Exception as e:
        return f"FAILED to call API: {str(e)}"

def execute_tool_by_name(tool_name: str, tool_args: dict) -> str:
    """Dynamically invokes a tool by its string name if it exists in the module scope."""
    if tool_name in globals() and hasattr(globals()[tool_name], "invoke"):
        tool_func = globals()[tool_name]
        return tool_func.invoke(tool_args)
    return f"ERROR: Tool '{tool_name}' not found or is not executable."

async def _async_call_jobs_mcp_tool(function_name: str, function_args: dict) -> str:
    # We call the python script 'jobs_mcp_server.py' using stdio
    server_params = StdioServerParameters(
        command="python",
        args=["jobs_mcp_server.py"],
        env=None
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # Call the specific tool exposed by jobs_mcp_server.py
                result = await session.call_tool(function_name, arguments=function_args)
                
                if hasattr(result, "content") and isinstance(result.content, list):
                    return "\n".join(item.text for item in result.content if hasattr(item, 'text'))
                return str(result)
    except Exception as e:
        return f"FAILED to call MCP Server: {str(e)}"

@tool
def get_job_status(job_id: str) -> str:
    """Get the current status of a given job ID. Use this to verify state before taking any administrative action."""
    return asyncio.run(_async_call_jobs_mcp_tool("get_job_status", {"job_id": job_id}))

@tool
def update_job_status(job_id: str, status: str) -> str:
    """Update job status. MUST provide 'status' argument (e.g. 'FAILED', 'ON_HOLD', 'SUCCESSFUL', 'RUNNING', 'FINISHED')."""
    return asyncio.run(_async_call_jobs_mcp_tool("update_job_status", {"job_id": job_id, "status": status}))

@tool
def get_job_log(job_id: str) -> str:
    """Retrieve the job log to determine why it failed or is stuck."""
    return asyncio.run(_async_call_jobs_mcp_tool("get_job_log", {"job_id": job_id}))
