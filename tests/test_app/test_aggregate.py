from dataclasses import dataclass

import pytest

from src.app.aggregate import AggregateRoot, apply_event
from src.app.errors import AggregateEventHandlerNotRegisteredError
from src.app.event import DomainEvent


@dataclass(frozen=True)
class SampleEvent(DomainEvent):
    __event__ = "test_event"
    foo: str = "bar"


class SampleAggregate(AggregateRoot):
    def __init__(self) -> None:
        super().__init__()
        self.foo = "foo"

    @apply_event
    def handle_test_event(self, event: SampleEvent) -> None:
        self.foo = event.foo


def test_register_event_applies_and_tracks_event():
    event = SampleEvent()
    agg = SampleAggregate()

    agg.register_event(event)

    assert agg.foo == "bar"
    assert agg.uncommitted_events == (event,)
    assert agg.version == 0


def test_replay_restores_state_without_registering_events():
    event = SampleEvent()
    agg = SampleAggregate()

    agg.replay([event])

    assert agg.foo == "bar"
    assert agg.uncommitted_events == ()
    assert agg.version == 1


def test_mark_committed_clears_events_and_updates_version():
    agg = SampleAggregate()
    agg.register_event(SampleEvent())

    agg.mark_committed()

    assert agg.uncommitted_events == ()
    assert agg.version == 1


def test_aggregate_registers_multiple_events_and_tracks():
    event_1 = SampleEvent()
    event_2 = SampleEvent()
    agg = SampleAggregate()

    agg.register_event(event_1)
    agg.register_event(event_2)

    assert agg.uncommitted_events == (event_1, event_2)
    assert agg.version == 0

    agg.mark_committed()

    assert agg.uncommitted_events == ()
    assert agg.version == 2


def test_aggregate_event_handler_not_registered():
    event = DomainEvent()
    agg = SampleAggregate()

    with pytest.raises(AggregateEventHandlerNotRegisteredError, match=type(event).__name__):
        agg.register_event(event)

    assert agg.uncommitted_events == ()
    assert agg.version == 0
