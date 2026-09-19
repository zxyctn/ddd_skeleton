from collections.abc import Callable
from typing import Any, TypeVar

from src.app.errors import (
    CommandHandlerAlreadyRegisteredError,
    CommandHandlerNotRegisteredError,
    QueryHandlerAlreadyRegisteredError,
    QueryHandlerNotRegisteredError,
)

T = TypeVar("T", bound=Callable[..., Any])


class Command:
    __command__: str


class Query:
    __query__: str


class Module:
    def __init__(self, name: str) -> None:
        self.name = name
        self._command_handlers: dict[str, Callable[..., Any]] = {}
        self._query_handlers: dict[str, Callable[..., Any]] = {}

    def on_command(self, command: type[Command]) -> Callable[[T], T]:
        def decorator(handler: T) -> T:
            if command.__command__ in self._command_handlers:
                raise CommandHandlerAlreadyRegisteredError(name=command.__command__)

            self._command_handlers[command.__command__] = handler
            return handler

        return decorator

    def on_query(self, query: type[Query]) -> Callable[[T], T]:
        def decorator(handler: T) -> T:
            if query.__query__ in self._query_handlers:
                raise QueryHandlerAlreadyRegisteredError(name=query.__query__)

            self._query_handlers[query.__query__] = handler
            return handler

        return decorator

    async def handle_command(self, command: type[Command], data: Any) -> Any:
        try:
            handler = self._command_handlers[command.__command__]
        except KeyError:
            raise CommandHandlerNotRegisteredError(name=command.__command__) from None

        return await handler(data)

    async def handle_query(self, query: type[Query], data: Any) -> Any:
        try:
            handler = self._query_handlers[query.__query__]
        except KeyError:
            raise QueryHandlerNotRegisteredError(name=query.__query__) from None

        return await handler(data)
