from collections.abc import Callable
from uuid import UUID

from src.app.aggregate import AggregateRoot
from src.app.event_store import EventStore
from src.app.uow import UnitOfWork


class Repository[T: AggregateRoot]:
    async def get(self, aggregate_id: UUID) -> T:
        raise NotImplementedError

    async def save(self, aggregate: T) -> None:
        raise NotImplementedError


class EventSourcedRepository[T: AggregateRoot](Repository[T]):
    def __init__(
        self, event_store: EventStore, aggregate_factory: Callable[[UUID], T], uow: UnitOfWork
    ) -> None:
        self.event_store = event_store
        self.aggregate_factory = aggregate_factory
        self.uow = uow

    async def get(self, aggregate_id: UUID) -> T:
        events = await self.event_store.load(aggregate_id)

        aggregate = self.aggregate_factory(aggregate_id)
        aggregate.replay(events)

        return aggregate

    async def save(self, aggregate: T) -> None:
        await self.event_store.append(
            aggregate_id=aggregate.id,
            expected_version=aggregate.version,
            events=aggregate.uncommitted_events,
        )
        self.uow.mark_saved(aggregate)
