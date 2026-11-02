import asyncio
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main() -> None:
    server_file = Path(__file__).resolve().with_name("server.py")
    transport = StdioTransport(command=sys.executable, args=[str(server_file)])

    async with Client(transport) as client:
        tools = await client.list_tools()
        assert [tool.name for tool in tools] == ["find_runbook"]

        result = await client.call_tool("find_runbook", {"service": "worker"})
        assert result.data.status == "ok"
        assert result.data.service == "worker"

    print("stdio: find_runbook ok")


if __name__ == "__main__":
    asyncio.run(main())
