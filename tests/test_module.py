from collections.abc import Callable
from typing import Any

import pytest

from src.app.application import Application
from src.app.errors import (
    CommandHandlerAlreadyRegisteredError,
    CommandHandlerNotRegisteredError,
    QueryHandlerAlreadyRegisteredError,
    QueryHandlerNotRegisteredError,
)
from src.app.module import Command, Module, Query


@pytest.fixture
def registered_module(
    app: Application,
    module: Module,
    command: type[Command],
    query: type[Query],
    handler: Callable[..., Any],
) -> Module:
    module._command_handlers[command.__command__] = handler
    module._query_handlers[query.__query__] = handler
    app.add(module)
    return app.get(module.name)


def test_already_registered_command_handler(registered_module, command):
    with pytest.raises(
        CommandHandlerAlreadyRegisteredError,
        match=rf"already registered for command: {command.__command__}",
    ):

        @registered_module.on_command(command)
        def test():
            pass


async def test_nonexistent_command_dispatch(module, command):
    with pytest.raises(
        CommandHandlerNotRegisteredError,
        match=rf"not registered for command: {command.__command__}",
    ):
        await module.handle_command(command, "test")


def test_already_registered_query_handler(registered_module, query):
    with pytest.raises(
        QueryHandlerAlreadyRegisteredError,
        match=rf"already registered for query: {query.__query__}",
    ):

        @registered_module.on_query(query)
        def test():
            pass


async def test_nonexistent_query_dispatch(module, query):
    with pytest.raises(
        QueryHandlerNotRegisteredError, match=rf"not registered for query: {query.__query__}"
    ):
        await module.handle_query(query, "test")


async def test_command_dispatch(registered_module, command, handler):
    result = await registered_module.handle_command(command, "test")

    assert result == "handled"
    assert command.__command__ in registered_module._command_handlers
    assert handler == registered_module._command_handlers[command.__command__]


async def test_query_dispatch(registered_module, query, handler):
    result = await registered_module.handle_query(query, "test")

    assert result == "handled"
    assert query.__query__ in registered_module._query_handlers
    assert handler == registered_module._query_handlers[query.__query__]
