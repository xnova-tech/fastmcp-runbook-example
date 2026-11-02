import asyncio
import subprocess
import sys
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from fastmcp.exceptions import ToolError

from server import RunbookResult, find_runbook, mcp

ROOT = Path(__file__).resolve().parents[1]


def test_python_function_returns_typed_results() -> None:
    found = find_runbook("api")
    missing = find_runbook("unknown")

    assert found == RunbookResult(
        service="api",
        status="ok",
        hint="Проверьте HTTP-статус, журнал и подключение к базе.",
    )
    assert missing.status == "not_found"
    assert missing.hint == "Сервис не найден."


def test_in_memory_discovery_schema_and_calls() -> None:
    async def scenario() -> None:
        async with Client(mcp) as client:
            tools = await client.list_tools()
            assert [tool.name for tool in tools] == ["find_runbook"]
            schema = tools[0].input_schema
            assert schema["properties"]["service"]["type"] == "string"
            assert schema["required"] == ["service"]
            output_schema = tools[0].output_schema
            assert output_schema["properties"]["status"]["enum"] == [
                "ok",
                "not_found",
            ]

            found = await client.call_tool("find_runbook", {"service": "api"})
            assert found.data.status == "ok"
            assert found.data.service == "api"

            missing = await client.call_tool(
                "find_runbook", {"service": "unknown"}
            )
            assert missing.data.status == "not_found"

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("arguments", "error_code"),
    [
        ({"service": 123}, "string_type"),
        ({}, "missing_argument"),
        ({"service": "api", "extra": True}, "unexpected_keyword_argument"),
    ],
)
def test_invalid_arguments_are_rejected(
    arguments: dict[str, object], error_code: str
) -> None:
    async def scenario() -> None:
        async with Client(mcp) as client:
            with pytest.raises(ToolError, match=error_code):
                await client.call_tool("find_runbook", arguments)

    asyncio.run(scenario())


def test_unknown_tool_is_rejected() -> None:
    async def scenario() -> None:
        async with Client(mcp) as client:
            with pytest.raises(ToolError, match="Unknown tool: 'missing_tool'"):
                await client.call_tool("missing_tool", {})

    asyncio.run(scenario())


def test_stdio_discovers_and_calls_tool() -> None:
    async def scenario() -> None:
        transport = StdioTransport(
            command=sys.executable,
            args=[str(ROOT / "server.py")],
        )
        async with Client(transport) as client:
            tools = await client.list_tools()
            assert [tool.name for tool in tools] == ["find_runbook"]
            result = await client.call_tool(
                "find_runbook", {"service": "worker"}
            )
            assert result.data.status == "ok"
            assert result.data.service == "worker"

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("script", "expected_stdout"),
    [
        (
            "smoke.py",
            "tools: find_runbook\nknown: ok\nunknown: not_found\n",
        ),
        ("stdio_smoke.py", "stdio: find_runbook ok\n"),
    ],
)
def test_smoke_scripts_have_stable_stdout(
    script: str, expected_stdout: str
) -> None:
    completed = subprocess.run(
        [sys.executable, str(ROOT / script)],
        capture_output=True,
        check=False,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout == expected_stdout


def test_stdio_connection_error_is_reported() -> None:
    async def scenario() -> None:
        transport = StdioTransport(
            command="/definitely/missing/python",
            args=[str(ROOT / "server.py")],
        )
        with pytest.raises(RuntimeError, match="Client failed to connect"):
            async with Client(transport):
                pass

    asyncio.run(scenario())
