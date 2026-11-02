# FastMCP-сервер с runbook-инструментом

Минимальный локальный пример XNova на Python: сервер объявляет инструмент `find_runbook(service)`, а два клиента проверяют его в памяти и через настоящий `stdio` subprocess. Модель, API-ключи, Docker и внешние сервисы не нужны.

Проект использует самостоятельную библиотеку `fastmcp==4.0.5`. Это не пример импорта из официального пакета `mcp`: здесь сервер создаётся через `from fastmcp import FastMCP`.

## Что понадобится

- Python 3.12;
- Git для клонирования проекта;
- терминал.

## Установка

```bash
git clone https://github.com/xnova-tech/fastmcp-runbook-example.git
cd fastmcp-runbook-example
python3.12 -m venv .venv
```

Активируйте окружение:

- macOS и Linux: `source .venv/bin/activate`;
- Windows PowerShell: `.venv\Scripts\Activate.ps1`;
- Windows cmd: `.venv\Scripts\activate.bat`.

Установите закреплённые зависимости:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
```

## Запуск проверок

Проверка в памяти не создаёт отдельный процесс:

```bash
python smoke.py
```

Ожидаемый stdout:

```text
tools: find_runbook
known: ok
unknown: not_found
```

Проверка `stdio` запускает `server.py` как дочерний процесс:

```bash
python stdio_smoke.py
```

Ожидаемый stdout:

```text
stdio: find_runbook ok
```

FastMCP может вывести стартовый баннер сервера в `stderr`; протокольный `stdout` при этом остаётся чистым.

Полный регрессионный набор:

```bash
python -m pytest -q
```

Тесты проверяют обнаружение инструмента, входную и выходную схемы, успешные вызовы, неизвестный сервис, неверные аргументы, неизвестный tool, отдельный `stdio`-процесс, стабильный stdout обоих smoke-скриптов и ошибку подключения.

## Структура

- `server.py` — FastMCP-сервер и типизированный результат `RunbookResult`;
- `smoke.py` — короткий in-memory roundtrip;
- `stdio_smoke.py` — roundtrip через дочерний процесс;
- `tests/test_fastmcp.py` — полный pytest-контракт;
- `.github/workflows/check.yml` — проверки на Linux, macOS и Windows.

Проект предназначен для локального учебного запуска. Он не открывает HTTP-порт, не читает пользовательские файлы и не выполняет изменяющих операций.

Автор: XNova.
