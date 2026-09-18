from src.main import example_app
from src.modules.example.application.command_handlers import ping as ping_command_handler
from src.modules.example.application.commands import PingCommand
from src.modules.example.application.queries import PingQuery
from src.modules.example.application.query_handlers import ping as ping_query_handler


async def test_command_dispatch():
    result = await example_app.handle_command(PingCommand, "hello")

    assert result == "pong: hello"
    assert PingCommand in example_app._command_handlers
    assert ping_command_handler == example_app._command_handlers[PingCommand]


async def test_query_dispatch():
    result = await example_app.handle_query(PingQuery, "hi")

    assert result == "pong: hi"
    assert PingQuery in example_app._query_handlers
    assert ping_query_handler == example_app._query_handlers[PingQuery]
