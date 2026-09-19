from collections.abc import Callable
from typing import Any

import pytest

from src.app.application import Application
from src.app.module import Command, Module, Query


@pytest.fixture
def app() -> Application:
    return Application()


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
    async def _handler(_: str) -> str:
        return "handled"

    return _handler
