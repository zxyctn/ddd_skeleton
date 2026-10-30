from uuid import UUID

from src.app.errors import ConcurrencyError
from src.app.event import DomainEvent
from src.app.event_store import EventStore


class FakeEventStore(EventStore):
    def __init__(self):
        self._streams: dict[UUID, tuple[DomainEvent, ...]] = {}

    async def load(self, aggregate_id: UUID) -> tuple[DomainEvent, ...]:
        return self._streams.get(aggregate_id, ())

    async def append(
        self,
        aggregate_id: UUID,
        expected_version: int,
        events: tuple[DomainEvent, ...],
    ) -> None:
        current = await self.load(aggregate_id)

        if len(current) != expected_version:
            raise ConcurrencyError(
                aggregate_id=aggregate_id,
                actual=len(current),
                expected=expected_version,
            )

        self._streams[aggregate_id] = current + events
