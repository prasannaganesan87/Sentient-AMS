import asyncio
import httpx
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("Jobs Management", dependencies=["httpx"])

BASE_URL = "http://localhost:8001/jobs"

@mcp.tool()
async def get_job_status(job_id: str) -> str:
    """Get the current status of a given job ID."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/{job_id}/status")
            if response.status_code == 200:
                data = response.json()
                return f"Job {data['job_id']} status is {data['status']}"
            elif response.status_code == 404:
                return f"Job {job_id} not found."
            else:
                return f"Error getting status: {response.text}"
        except Exception as e:
            return f"Failed to connect to Jobs API: {str(e)}"

@mcp.tool()
async def update_job_status(job_id: str, status: str) -> str:
    """
    Update the status of a job.
    VALID_STATUSES = ["RUNNING", "ON_HOLD", "FAILED", "SUCCESSFUL", "FINISHED", "WAITING"]
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(f"{BASE_URL}/{job_id}/status", json={"status": status.upper()})
            if response.status_code == 200:
                data = response.json()
                return data.get("message", f"Job status updated to {status}")
            else:
                return f"Error updating status: {response.text}"
        except Exception as e:
            return f"Failed to connect to Jobs API: {str(e)}"

@mcp.tool()
async def get_job_log(job_id: str) -> str:
    """Get the log output for a given job ID."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/{job_id}/log")
            if response.status_code == 200:
                data = response.json()
                return f"Job {job_id} log:\n{data['log']}"
            elif response.status_code == 404:
                return f"Job {job_id} not found."
            else:
                return f"Error getting log: {response.text}"
        except Exception as e:
            return f"Failed to connect to Jobs API: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
