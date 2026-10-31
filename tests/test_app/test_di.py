from typing import Protocol

import pytest

from src.app.errors import DependencyAlreadyRegistered, DependencyNotRegistered
from tests.fakes.uow import FakeUnitOfWork


class Port(Protocol):
    def foo(self, input: str) -> str: ...


class Adapter:
    def foo(self, input: str) -> str:
        return f"bar: {input}"


def test_di_dependency_resolves(di):
    di.register(Port, lambda: Adapter())
    assert type(di.resolve(Port)) is Adapter


def test_di_dependency_already_registered(di):
    di.register(Port, lambda: Adapter())

    with pytest.raises(DependencyAlreadyRegistered, match=Port.__name__):
        di.register(Port, lambda: Adapter())


def test_di_dependency_not_registered(di):
    with pytest.raises(DependencyNotRegistered, match=Port.__name__):
        di.resolve(Port)


async def test_di_scoped_dependency_reuses_instance(di):
    di.register(FakeUnitOfWork, FakeUnitOfWork, scoped=True)

    async with di.scope():
        first = di.resolve(FakeUnitOfWork)
        second = di.resolve(FakeUnitOfWork)

        assert first is second


async def test_di_different_scopes_use_different_instances(di):
    di.register(FakeUnitOfWork, FakeUnitOfWork, scoped=True)

    async with di.scope():
        first = di.resolve(FakeUnitOfWork)

    async with di.scope():
        second = di.resolve(FakeUnitOfWork)

    assert first is not second
