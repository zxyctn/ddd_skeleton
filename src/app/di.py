from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any, TypeVar, cast

from src.app.errors import DependencyAlreadyRegistered, DependencyNotRegistered

T = TypeVar("T")


class DI:
    def __init__(self) -> None:
        self._providers: dict[type[Any], Callable[[], Any]] = {}
        self._scope: ContextVar[dict[type[Any], Any] | None] = ContextVar(
            "di_scope",
            default=None,
        )
        self._scoped: set[type[Any]] = set()

    def register(
        self, dependency: type[T], provider: Callable[[], T], *, scoped: bool = False
    ) -> None:
        if dependency in self._providers:
            raise DependencyAlreadyRegistered(name=dependency.__name__)

        self._providers[dependency] = provider

        if scoped:
            self._scoped.add(dependency)

    def resolve(self, dependency: type[T]) -> T:
        try:
            provider: Callable[[], T] = self._providers[dependency]
        except KeyError:
            raise DependencyNotRegistered(name=dependency.__name__) from None

        scope = self._scope.get()
        if scope is not None and dependency in self._scoped:
            if dependency not in scope:
                scope[dependency] = provider()
            return cast(T, scope[dependency])

        return provider()

    @asynccontextmanager
    async def scope(self) -> AsyncGenerator[None, None]:
        token = self._scope.set({})

        try:
            yield
        finally:
            self._scope.reset(token)
