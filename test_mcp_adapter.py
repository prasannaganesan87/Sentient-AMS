import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

servers_config = {
    "jobs-mcp": {
        "command": "python",
        "args": ["jobs_mcp_server.py"],
        "transport": "stdio",
    }
}

async def main():
    client = MultiServerMCPClient(servers_config)
    tools = await client.get_tools()
    print("Tools fetched:", [t.name for t in tools])
    try:
        # Try invoking one tool
        tool = next(t for t in tools if t.name == "get_job_status")
        # Since tools are LangChain tools, we can try sync invoke
        res = tool.invoke({"job_id": "JOB-002"})
        print("Success!", res)
    except Exception as e:
        print("Failed:", str(e))

asyncio.run(main())
