from typing import Protocol

import pytest

from src.app.errors import (
    CommandHandlerAlreadyRegisteredError,
    CommandHandlerNotRegisteredError,
    DependencyNotRegistered,
    QueryHandlerAlreadyRegisteredError,
    QueryHandlerNotRegisteredError,
)
from src.app.uow import UnitOfWork
from tests.fakes.uow import FakeUnitOfWork


class Port(Protocol):
    def foo(self, input: str) -> str: ...


class Adapter:
    def foo(self, input: str) -> str:
        return f"bar: {input}"


class Separator(Protocol):
    def separate(self, items: list[str]) -> str: ...


class CommaSeparator:
    def separate(self, items: list[str]) -> str:
        return ", ".join(items)


class SemicolonSeparator:
    def separate(self, items: list[str]) -> str:
        return "; ".join(items)


class TestCommands:
    @pytest.fixture
    def module(self, module):
        module.provide(UnitOfWork, FakeUnitOfWork)
        return module

    def test_already_registered_command_handler(self, module, command, handler):
        module.on_command(command)(handler)
        with pytest.raises(
            CommandHandlerAlreadyRegisteredError,
            match=rf"already registered for command: {command.__command__}",
        ):

            @module.on_command(command)
            def test():
                pass

    async def test_nonexistent_command_dispatch(self, module, command):
        with pytest.raises(
            CommandHandlerNotRegisteredError,
            match=rf"not registered for command: {command.__command__}",
        ):
            await module.handle_command(command, "test")

    async def test_command_dispatch(self, module, command, handler):
        module.on_command(command)(handler)
        result = await module.handle_command(command, data="test")

        assert result == "handled"
        assert module.get_command_handler(command) is handler

    async def test_command_di_resolves(self, module, command):
        module.provide(Port, lambda: Adapter())

        @module.on_command(command)
        async def handler(data: str, adapter: Port):
            return adapter.foo(data)

        result = await module.handle_command(command, data="test")
        assert result == "bar: test"

    async def test_command_di_overrides(self, module, command):
        module.provide(Port, lambda: Adapter())
        module.provide(Separator, lambda: CommaSeparator())

        @module.on_command(command)
        async def handler(data: list[str], adapter: Port, separator: Separator):
            return adapter.foo(separator.separate(items=data))

        default_result = await module.handle_command(command, data=["John", "Jane"])
        overridden_result = await module.handle_command(
            command, data=["John", "Jane"], separator=SemicolonSeparator()
        )

        assert default_result == "bar: John, Jane"
        assert overridden_result == "bar: John; Jane"

    async def test_command_di_raises_for_missing_provider(self, module, command):
        @module.on_command(command)
        async def handle_command(data: str, adapter: Port):
            return adapter.foo(data)

        with pytest.raises(DependencyNotRegistered, match=Port.__name__):
            await module.handle_command(command, data="test")

    async def test_handler_raises_for_missing_annotation(self, module, command):
        @module.on_command(command)
        async def handler(data, dependency):
            return "handled"

        with pytest.raises(TypeError, match="Missing type annotation"):
            await module.handle_command(command, data="test")


class TestQueries:
    def test_already_registered_query_handler(self, module, query, handler):
        module.on_query(query)(handler)
        with pytest.raises(
            QueryHandlerAlreadyRegisteredError,
            match=rf"already registered for query: {query.__query__}",
        ):

            @module.on_query(query)
            def test():
                pass

    async def test_nonexistent_query_dispatch(self, module, query):
        with pytest.raises(
            QueryHandlerNotRegisteredError,
            match=rf"not registered for query: {query.__query__}",
        ):
            await module.handle_query(query, "test")

    async def test_query_dispatch(self, module, query, handler):
        module.on_query(query)(handler)
        result = await module.handle_query(query, data="test")

        assert result == "handled"
        assert module.get_query_handler(query) is handler

    async def test_query_di_resolves(self, module, query):
        module.provide(Port, lambda: Adapter())

        @module.on_query(query)
        async def handle_query(data: str, adapter: Port):
            return adapter.foo(data)

        result = await module.handle_query(query, data="test")
        assert result == "bar: test"

    async def test_query_di_overrides(self, module, query):
        module.provide(Port, lambda: Adapter())
        module.provide(Separator, lambda: CommaSeparator())

        @module.on_query(query)
        async def handle_query(data: list[str], adapter: Port, separator: Separator):
            return adapter.foo(separator.separate(items=data))

        default_result = await module.handle_query(query, data=["John", "Jane"])
        overridden_result = await module.handle_query(
            query, data=["John", "Jane"], separator=SemicolonSeparator()
        )

        assert default_result == "bar: John, Jane"
        assert overridden_result == "bar: John; Jane"

    async def test_query_di_raises_for_missing_provider(self, module, query):
        @module.on_query(query)
        async def handle_query(data: str, adapter: Port):
            return adapter.foo(data)

        with pytest.raises(DependencyNotRegistered, match=Port.__name__):
            await module.handle_query(query, data="test")


class TestEvents:
    async def test_event_handlers_registered(self, module, event):
        handled: list[str] = []

        @module.on_event(type(event))
        async def handler_a():
            handled.append("handler_a")

        @module.on_event(type(event))
        async def handler_b():
            handled.append("handler_b")

        await module.dispatch_event(event)

        handlers = module.get_event_handlers(event)

        assert len(handlers) == 2
        assert handler_a in handlers
        assert handler_b in handlers
        assert handled == ["handler_a", "handler_b"]

    async def test_event_handler_receives_event(self, module, event_type):
        result = ""
        event = event_type(foo="not bar")

        @module.on_event(event_type)
        async def handler(data):
            nonlocal result
            result = f"foo is {data.foo}"

            assert isinstance(data, event_type)

        await module.dispatch_event(event)

        assert result == f"foo is {event.foo}"

    async def test_event_handler_di_resolves(self, module, event_type):
        result = ""
        event = event_type(foo="test")

        module.provide(Port, lambda: Adapter())

        @module.on_event(event_type)
        async def handler(data, adapter: Port):
            nonlocal result
            result = adapter.foo(data.foo)

        await module.dispatch_event(event)

        assert result == "bar: test"
