import inspect
from collections.abc import Callable, Iterable
from typing import get_type_hints
from uuid import UUID

from src.app.errors import AggregateEventHandlerNotRegisteredError
from src.app.event import DomainEvent


def apply_event[F: Callable[..., None]](handler: F) -> F:
    handler.__dict__["__applies_event__"] = True
    return handler


class AggregateRoot:
    def __init__(self, aggregate_id: UUID) -> None:
        self._version = 0
        self._uncommitted_events: list[DomainEvent] = []
        self.id = aggregate_id

    @property
    def version(self) -> int:
        return self._version

    @property
    def uncommitted_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._uncommitted_events)

    @property
    def event_handlers(self) -> tuple[Callable[..., None], ...]:
        return tuple(
            handler
            for _, handler in inspect.getmembers(type(self), inspect.isfunction)
            if getattr(handler, "__applies_event__", False)
        )

    def _get_event_handler(self, event: DomainEvent) -> Callable[..., None]:
        for handler in self.event_handlers:
            if get_type_hints(handler).get("event") is type(event):
                return handler

        raise AggregateEventHandlerNotRegisteredError(name=type(event).__name__)

    def _apply_event(self, event: DomainEvent) -> None:
        handler = self._get_event_handler(event)
        handler(self, event)

    def register_event(self, event: DomainEvent) -> None:
        self._apply_event(event)
        self._uncommitted_events.append(event)

    def replay(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            self._apply_event(event)
            self._version += 1

    def mark_committed(self) -> None:
        self._version += len(self._uncommitted_events)
        self._uncommitted_events.clear()
