from collections.abc import Callable
from uuid import UUID

from src.app.aggregate import AggregateRoot
from src.app.event_store import EventStore


class Repository[T: AggregateRoot]:
    async def get(self, aggregate_id: UUID) -> T:
        raise NotImplementedError

    async def save(self, aggregate: T) -> None:
        raise NotImplementedError


class EventSourcedRepository[T: AggregateRoot](Repository[T]):
    def __init__(
        self,
        event_store: EventStore,
        aggregate_factory: Callable[[UUID], T],
    ) -> None:
        self.event_store = event_store
        self.aggregate_factory = aggregate_factory

    async def get(self, aggregate_id: UUID) -> T:
        events = await self.event_store.load(aggregate_id)

        aggregate = self.aggregate_factory(aggregate_id)
        aggregate.replay(events)

        return aggregate
