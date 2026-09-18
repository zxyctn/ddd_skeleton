from src.modules.example.application.queries import PingQuery
from src.modules.example.entrypoint import example


@example.on_query(PingQuery)
async def ping(data: PingQuery.Request) -> PingQuery.Response:
    return f"pong: {data}"
