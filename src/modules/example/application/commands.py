from src.app.module import Command


class PingCommand(Command):
    __command__ = "ping"

    type Request = str
    type Response = str
