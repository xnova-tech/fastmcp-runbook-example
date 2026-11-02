from typing import Literal

from fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("Runbook Demo")

RUNBOOKS: dict[str, str] = {
    "api": "Проверьте HTTP-статус, журнал и подключение к базе.",
    "worker": "Проверьте очередь задач и ошибки обработки.",
}


class RunbookResult(BaseModel):
    service: str
    status: Literal["ok", "not_found"]
    hint: str


@mcp.tool
def find_runbook(service: str) -> RunbookResult:
    """Возвращает первую диагностическую проверку для сервиса."""
    if service not in RUNBOOKS:
        return RunbookResult(
            service=service,
            status="not_found",
            hint="Сервис не найден.",
        )
    return RunbookResult(service=service, status="ok", hint=RUNBOOKS[service])


if __name__ == "__main__":
    mcp.run()
