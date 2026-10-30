from collections.abc import Iterable

from src.app.event import DomainEvent


class AggregateRoot:
    def __init__(self) -> None:
        self._version = 0
        self._uncommitted_events: list[DomainEvent] = []

    @property
    def version(self) -> int:
        return self._version

    @property
    def uncommitted_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._uncommitted_events)

    def register_event(self, event: DomainEvent) -> None:
        self._apply_event(event)
        self._uncommitted_events.append(event)

    def replay(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            self._apply_event(event)
            self._version += 1

    def _apply_event(self, event: DomainEvent) -> None:
        raise NotImplementedError

    def mark_committed(self) -> None:
        self._version += len(self._uncommitted_events)
        self._uncommitted_events.clear()
