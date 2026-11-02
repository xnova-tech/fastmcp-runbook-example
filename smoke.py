import asyncio

from fastmcp import Client

from server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        names = sorted(tool.name for tool in tools)
        assert names == ["find_runbook"], names

        found = await client.call_tool("find_runbook", {"service": "api"})
        assert found.data.status == "ok"

        missing = await client.call_tool("find_runbook", {"service": "unknown"})
        assert missing.data.status == "not_found"

    print("tools: find_runbook")
    print("known: ok")
    print("unknown: not_found")


if __name__ == "__main__":
    asyncio.run(main())
