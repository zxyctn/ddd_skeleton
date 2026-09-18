from src.app.module import Module

example = Module("example")

from src.modules.example.application import (
    command_handlers,  # noqa: E402, F401
    query_handlers,  # noqa: E402, F401
)
