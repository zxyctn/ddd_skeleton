import pytest

from src.app.errors import HandlerAlreadyRegisteredError, HandlerNotFoundError
from src.main import example_app
from src.modules.example.application.command_handlers import ping as ping_command_handler
from src.modules.example.application.commands import PingCommand
from src.modules.example.application.queries import PingQuery
from src.modules.example.application.query_handlers import ping as ping_query_handler


async def test_registered_command_handler():
    with pytest.raises(HandlerAlreadyRegisteredError):

        @example_app.on_command(PingCommand)
        def test():
            pass


async def test_nonexistent_command_dispatch():
    class TestCommand:
        __name__ = "test"

        type Request = str
        type Response = str

    with pytest.raises(HandlerNotFoundError):
        await example_app.handle_command(TestCommand, "hello")


async def test_registered_query_handler():
    with pytest.raises(HandlerAlreadyRegisteredError):

        @example_app.on_query(PingQuery)
        def test():
            pass


async def test_nonexistent_query_dispatch():
    class TestQuery:
        __name__ = "test"

        type Request = str
        type Response = str

    with pytest.raises(HandlerNotFoundError):
        await example_app.handle_query(TestQuery, "hello")


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
