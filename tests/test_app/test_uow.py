from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest

from src.app.aggregate import apply_event
from src.app.event import DomainEvent
from src.app.module import Command, Module
from src.app.repository import EventSourcedRepository
from src.app.uow import UnitOfWork
from tests.fakes.aggregate import FakeAggregate
from tests.fakes.event_store import FakeEventStore
from tests.fakes.uow import FakeUnitOfWork


@pytest.fixture
def module(module, uow):
    module.provide(UnitOfWork, lambda: uow, scoped=True)
    return module


async def test_uow_commits(uow, module, command, handler):
    module.on_command(command)(handler)
    await module.handle_command(command, data="test")
    assert uow.began is True
    assert uow.committed is True
    assert uow.rolled_back is False


async def test_uow_rolls_back_when_handler_fails(uow, module, command):
    @module.on_command(command)
    async def handler(data):
        raise Exception("test")

    with pytest.raises(Exception, match="test"):
        await module.handle_command(command, data="test")

    assert uow.began is True
    assert uow.committed is False
    assert uow.rolled_back is True


@dataclass(frozen=True)
class UpdateFooEvent(DomainEvent):
    __event__ = "foo_updated"
    foo: str


class SampleAggregate(FakeAggregate):
    def update_foo(self, foo: str):
        self.register_event(UpdateFooEvent(foo=foo))

    @apply_event
    def foo_updated(self, event: UpdateFooEvent):
        self.foo = event.foo


@dataclass(frozen=True)
class UpdateFooRequest:
    id: UUID
    foo: str


class UpdateFooCommand(Command):
    __command__ = "update_foo"
    type Request = UpdateFooRequest


async def test_uow_rolls_back_when_handler_succeeds_commit_fails():
    module = Module(name="test")
    store = FakeEventStore()
    uow = FakeUnitOfWork(fail_commit=True)
    repo = EventSourcedRepository(event_store=store, aggregate_factory=SampleAggregate, uow=uow)

    module.provide(UnitOfWork, lambda: uow, scoped=True)
    module.provide(EventSourcedRepository, lambda: repo)

    saved_aggregate = None

    @module.on_command(UpdateFooCommand)
    async def handler(data: UpdateFooCommand.Request, repo: EventSourcedRepository):
        nonlocal saved_aggregate

        agg = await repo.get(data.id)
        agg.update_foo(foo=data.foo)
        await repo.save(agg)

        saved_aggregate = agg

    with pytest.raises(RuntimeError, match="Commit failed"):
        await module.handle_command(
            UpdateFooCommand,
            data=UpdateFooRequest(id=uuid4(), foo="updated"),
        )

    assert saved_aggregate is not None
    assert saved_aggregate.uncommitted_events
    assert saved_aggregate.version == 0
    assert uow.began is True
    assert uow.committed is False
    assert uow.rolled_back is True
    assert len(uow._saved_aggregates) == 0
