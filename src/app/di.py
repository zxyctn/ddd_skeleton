from collections.abc import Callable
from typing import Any, TypeVar

from src.app.errors import DependencyAlreadyRegistered, DependencyNotRegistered

T = TypeVar("T")


class DI:
    def __init__(self) -> None:
        self._providers: dict[type[Any], Callable[[], Any]] = {}

    def register(self, dependency: type[T], provider: Callable[[], T]) -> None:
        if dependency in self._providers:
            raise DependencyAlreadyRegistered(name=dependency.__name__)
        self._providers[dependency] = provider

    def resolve(self, dependency: type[T]) -> T:
        try:
            provider: Callable[[], T] = self._providers[dependency]
        except KeyError:
            raise DependencyNotRegistered(name=dependency.__name__) from None
        return provider()
