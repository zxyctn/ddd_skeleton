from dataclasses import dataclass
from uuid import uuid4

import pytest

from src.app.aggregate import apply_event
from src.app.errors import AggregateEventHandlerNotRegisteredError
from src.app.event import DomainEvent
from src.app.repository import EventSourcedRepository
from tests.fakes.aggregate import FakeAggregate
from tests.fakes.event_store import FakeEventStore
from tests.fakes.uow import FakeUnitOfWork


@dataclass(frozen=True)
class SampleEvent(DomainEvent):
    __event__ = "test_event"
    foo: str = "bar"


class SampleAggregate(FakeAggregate):
    @apply_event
    def handle_test_event(self, event: SampleEvent) -> None:
        self.foo = event.foo


@pytest.fixture
def aggregate():
    return SampleAggregate(uuid4())


def test_register_event_applies_and_tracks_event(aggregate):
    event = SampleEvent()

    aggregate.register_event(event)
    assert aggregate.foo == "bar"
    assert aggregate.uncommitted_events == (event,)
    assert aggregate.version == 0


def test_replay_restores_state_without_registering_events(aggregate):
    event = SampleEvent()

    aggregate.replay([event])
    assert aggregate.foo == "bar"
    assert aggregate.uncommitted_events == ()
    assert aggregate.version == 1


def test_mark_committed_clears_events_and_updates_version(aggregate):
    aggregate.register_event(SampleEvent())
    aggregate.mark_committed()

    assert aggregate.uncommitted_events == ()
    assert aggregate.version == 1


def test_aggregate_registers_multiple_events_and_tracks(aggregate):
    event_1 = SampleEvent()
    event_2 = SampleEvent()

    aggregate.register_event(event_1)
    aggregate.register_event(event_2)

    assert aggregate.uncommitted_events == (event_1, event_2)
    assert aggregate.version == 0

    aggregate.mark_committed()

    assert aggregate.uncommitted_events == ()
    assert aggregate.version == 2


def test_aggregate_event_handler_not_registered(aggregate):
    event = DomainEvent()

    with pytest.raises(AggregateEventHandlerNotRegisteredError, match=type(event).__name__):
        aggregate.register_event(event)

    assert aggregate.uncommitted_events == ()
    assert aggregate.version == 0


async def test_repo_returns_aggregate():
    store = FakeEventStore()
    repo = EventSourcedRepository(
        event_store=store, aggregate_factory=SampleAggregate, uow=FakeUnitOfWork()
    )
    event = SampleEvent(foo="updated")
    aggregate_id = uuid4()

    await store.append(aggregate_id, expected_version=0, events=(event,))

    aggregate = await repo.get(aggregate_id)

    assert isinstance(aggregate, SampleAggregate)
    assert aggregate.id == aggregate_id
    assert aggregate.foo == "updated"
    assert aggregate.version == 1
    assert aggregate.uncommitted_events == ()


@pytest.mark.asyncio
async def test_repo_saves_aggregate():
    store = FakeEventStore()
    repo = EventSourcedRepository(
        event_store=store, aggregate_factory=SampleAggregate, uow=FakeUnitOfWork()
    )
    aggregate_id = uuid4()
    aggregate = SampleAggregate(aggregate_id)
    event = SampleEvent()

    aggregate.register_event(event)
    await repo.save(aggregate)

    assert await store.load(aggregate_id) == (event,)
    assert aggregate.uncommitted_events == (event,)
    assert aggregate.version == 0
