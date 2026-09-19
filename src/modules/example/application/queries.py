from src.app.module import Query


class PingQuery(Query):
    __query__ = "ping"

    type Request = str
    type Response = str
