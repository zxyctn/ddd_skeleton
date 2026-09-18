from src.modules.example.application.commands import PingCommand
from src.modules.example.entrypoint import example


@example.on_command(PingCommand)
async def ping(data: PingCommand.Request) -> PingCommand.Response:
    return f"pong: {data}"
