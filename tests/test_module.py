from src.main import example_app
from src.modules.example.application.commands import Ping


async def test_command_dispatch():
    result = await example_app.handle_command(Ping, "hello")

    assert result == "pong: hello"
