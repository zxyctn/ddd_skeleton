from src.app.event import DomainEvent


class AggregateRoot:
    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    def register_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pop_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events
