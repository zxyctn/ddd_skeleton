from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest

from src.app.aggregate import AggregateRoot
from src.app.application import Application
from src.app.di import DI
from src.app.event import DomainEvent
from src.app.module import Command, Module, Query


@pytest.fixture
def app() -> Application:
    return Application()


@pytest.fixture
def di() -> DI:
    return DI()


@pytest.fixture
def module() -> Module:
    return Module(name="test_module")


@pytest.fixture
def command() -> type[Command]:
    class TestCommand(Command):
        __command__ = "test_command"

        type Request = str
        type Response = str

    return TestCommand


@pytest.fixture
def query() -> type[Query]:
    class TestQuery(Query):
        __query__ = "test_query"

        type Request = str
        type Response = str

    return TestQuery


@pytest.fixture
def handler() -> Callable[..., Any]:
    async def _handler(data: str) -> str:
        return "handled"

    return _handler


@pytest.fixture
def event_type() -> type[DomainEvent]:
    @dataclass(frozen=True)
    class TestEvent(DomainEvent):
        __event__ = "test_event"
        foo: str

    return TestEvent


@pytest.fixture
def event(event_type) -> DomainEvent:
    return event_type(foo="bar")


@pytest.fixture
def agg() -> AggregateRoot:
    return AggregateRoot()
