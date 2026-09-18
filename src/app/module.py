from collections.abc import Callable
from typing import Any, TypeVar

from src.app.errors import HandlerAlreadyRegisteredError, HandlerNotFoundError

T = TypeVar("T", bound=Callable[..., Any])


class Module:
    def __init__(self, name: str) -> None:
        self.name = name
        self._command_handlers: dict[type, Callable[..., Any]] = {}
        self._query_handlers: dict[type, Callable[..., Any]] = {}

    def on_command(self, command: type) -> Callable[[T], T]:
        def decorator(handler: T) -> T:
            if command in self._command_handlers:
                raise HandlerAlreadyRegisteredError(
                    f"Handler already registered for command {command.__name__}"
                )

            self._command_handlers[command] = handler
            return handler

        return decorator

    def on_query(self, query: type) -> Callable[[T], T]:
        def decorator(handler: T) -> T:
            if query in self._query_handlers:
                raise HandlerAlreadyRegisteredError(
                    f"Handler already registered for query {query.__name__}"
                )

            self._query_handlers[query] = handler
            return handler

        return decorator

    async def handle_command(self, command: type, data: Any) -> Any:
        try:
            handler = self._command_handlers[command]
        except KeyError:
            raise HandlerNotFoundError(
                f"No handler registered for command {command.__name__}"
            ) from None

        return await handler(data)

    async def handle_query(self, query: type, data: Any) -> Any:
        try:
            handler = self._query_handlers[query]
        except KeyError:
            raise HandlerNotFoundError(
                f"No handler registered for query {query.__name__}"
            ) from None

        return await handler(data)
