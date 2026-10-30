from uuid import uuid4

import pytest

from src.app.errors import ConcurrencyError
from src.app.event import DomainEvent


async def test_empty_stream(event_store):
    assert await event_store.load(uuid4()) == ()


async def test_appended_events_keep_same_order(event_store):
    aggregate_id = uuid4()
    events = (DomainEvent(), DomainEvent())

    await event_store.append(aggregate_id, expected_version=0, events=events)
    assert await event_store.load(aggregate_id) == events


async def test_appending_multiple_times(event_store):
    aggregate_id = uuid4()
    event_1 = DomainEvent()
    event_2 = DomainEvent()

    await event_store.append(aggregate_id, expected_version=0, events=(event_1,))
    assert await event_store.load(aggregate_id) == (event_1,)

    await event_store.append(aggregate_id, expected_version=1, events=(event_2,))
    assert await event_store.load(aggregate_id) == (event_1, event_2)


async def test_appending_incorrect_expected_version_raises(event_store):
    aggregate_id = uuid4()
    await event_store.append(aggregate_id, expected_version=0, events=(DomainEvent(),))

    with pytest.raises(ConcurrencyError, match="expected 0, actual 1"):
        await event_store.append(aggregate_id, expected_version=0, events=(DomainEvent(),))
