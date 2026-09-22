import inspect
from collections.abc import Callable
from typing import Any, TypeVar, get_type_hints

from src.app.di import DI
from src.app.errors import (
    CommandHandlerAlreadyRegisteredError,
    CommandHandlerNotRegisteredError,
    QueryHandlerAlreadyRegisteredError,
    QueryHandlerNotRegisteredError,
)
from src.app.event import DomainEvent

T = TypeVar("T")
C = TypeVar("C", bound=Callable[..., Any])


class Command:
    __command__: str


class Query:
    __query__: str


class Module:
    def __init__(self, name: str) -> None:
        self.name = name
        self._command_handlers: dict[str, Callable[..., Any]] = {}
        self._query_handlers: dict[str, Callable[..., Any]] = {}
        self._event_handlers: dict[str, list[Callable[..., Any]]] = {}
        self.di = DI()

    async def _invoke(
        self,
        handler: Callable[..., Any],
        data: Any,
        **overrides: Any,
    ) -> Any:
        signature = inspect.signature(handler)
        hints = get_type_hints(handler)
        kwargs: dict[str, Any] = {}

        for name, _ in signature.parameters.items():
            if name == "data":
                kwargs[name] = data
            elif name in overrides:
                kwargs[name] = overrides[name]
            elif name not in hints:
                raise TypeError(f"Missing type annotation for parameter: {name}")
            else:
                kwargs[name] = self.di.resolve(hints[name])

        return await handler(**kwargs)

    def get_command_handler(self, command: type[Command]) -> Callable[..., Any]:
        try:
            handler = self._command_handlers[command.__command__]
        except KeyError:
            raise CommandHandlerNotRegisteredError(name=command.__command__) from None
        return handler

    def get_query_handler(self, query: type[Query]) -> Callable[..., Any]:
        try:
            handler = self._query_handlers[query.__query__]
        except KeyError:
            raise QueryHandlerNotRegisteredError(name=query.__query__) from None
        return handler

    def get_event_handlers(self, event: DomainEvent) -> list[Callable[..., Any]]:
        return self._event_handlers.get(event.__event__, [])

    def on_command(self, command: type[Command]) -> Callable[[C], C]:
        def decorator(handler: C) -> C:
            if command.__command__ in self._command_handlers:
                raise CommandHandlerAlreadyRegisteredError(name=command.__command__)

            self._command_handlers[command.__command__] = handler
            return handler

        return decorator

    def on_query(self, query: type[Query]) -> Callable[[C], C]:
        def decorator(handler: C) -> C:
            if query.__query__ in self._query_handlers:
                raise QueryHandlerAlreadyRegisteredError(name=query.__query__)

            self._query_handlers[query.__query__] = handler
            return handler

        return decorator

    def on_event(self, event: type[DomainEvent]) -> Callable[[C], C]:
        def decorator(handler: C) -> C:
            self._event_handlers.setdefault(event.__event__, []).append(handler)
            return handler

        return decorator

    async def handle_command(self, command: type[Command], data: Any, **overrides: Any) -> Any:
        handler = self.get_command_handler(command)
        return await self._invoke(handler, data, **overrides)

    async def handle_query(self, query: type[Query], data: Any, **overrides: Any) -> Any:
        handler = self.get_query_handler(query)
        return await self._invoke(handler, data, **overrides)

    async def dispatch_event(self, event: DomainEvent, **overrides: Any) -> None:
        handlers = self.get_event_handlers(event)
        for handler in handlers:
            await self._invoke(handler, event, **overrides)

    def provide(self, dependency: type[T], provider: Callable[[], T]) -> None:
        self.di.register(dependency, provider)
