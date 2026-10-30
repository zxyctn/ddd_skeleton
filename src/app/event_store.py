from uuid import UUID

from src.app.event import DomainEvent


class EventStore:
    async def load(self, aggregate_id: UUID) -> tuple[DomainEvent, ...]:
        raise NotImplementedError

    async def append(
        self,
        aggregate_id: UUID,
        expected_version: int,
        events: tuple[DomainEvent, ...],
    ) -> None:
        raise NotImplementedError
