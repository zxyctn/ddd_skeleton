from src.modules.example.application.commands import Ping
from src.modules.example.entrypoint import example


@example.on_command(Ping)
async def ping(data: str) -> str:
    return f"pong: {data}"
