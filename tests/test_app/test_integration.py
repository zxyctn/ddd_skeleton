from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest

from src.app.aggregate import apply_event
from src.app.event import DomainEvent
from src.app.module import Command
from src.app.repository import EventSourcedRepository
from src.app.uow import UnitOfWork
from tests.fakes.aggregate import FakeAggregate
from tests.fakes.event_store import FakeEventStore
from tests.fakes.uow import FakeUnitOfWork


@pytest.fixture
def store():
    return FakeEventStore()


@pytest.fixture
def module(module, store):
    module.provide(UnitOfWork, FakeUnitOfWork, scoped=True)
    module.provide(
        EventSourcedRepository,
        lambda: EventSourcedRepository(
            event_store=store,
            aggregate_factory=SampleAggregate,
            uow=module.di.resolve(UnitOfWork),
        ),
    )
    return module


@dataclass(frozen=True)
class UpdateFooPayload:
    aggregate_id: UUID
    foo: str


class UpdateFoo(Command):
    __command__ = "fake_command"

    type Request = UpdateFooPayload
    type Response = None


@dataclass(frozen=True)
class FooUpdated(DomainEvent):
    __event__ = "foo_updated"
    foo: str


class SampleAggregate(FakeAggregate):
    def update_foo(self, foo: str) -> None:
        self.register_event(FooUpdated(foo=foo))

    @apply_event
    def on_foo_updated(self, event: FooUpdated) -> None:
        self.foo = event.foo


class TestCommands:
    async def test_command_and_repo_use_same_uow(self, module, command):
        @module.on_command(command)
        async def handler(data, repo: EventSourcedRepository, uow: UnitOfWork):
            assert uow is repo.uow

        await module.handle_command(command, None)

    async def test_command_full_lifecycle(self, module, store):
        saved = []

        @module.on_command(UpdateFoo)
        async def handler(data: UpdateFoo.Request, repo: EventSourcedRepository):
            agg = await repo.get(data.aggregate_id)
            agg.update_foo(data.foo)
            await repo.save(agg)
            saved.append(agg)

        aggregate_id = uuid4()
        initial_event = FooUpdated(foo="initial")

        await store.append(aggregate_id, 0, (initial_event,))
        await module.handle_command(
            UpdateFoo,
            UpdateFooPayload(aggregate_id=aggregate_id, foo="baz"),
        )
        events = await store.load(aggregate_id)

        assert saved[0].foo == "baz"
        assert saved[0].version == 2
        assert saved[0].uncommitted_events == ()
        assert [event.foo for event in events] == ["initial", "baz"]
