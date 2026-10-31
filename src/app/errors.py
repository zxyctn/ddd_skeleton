from typing import Literal
from uuid import UUID


class ModuleAlreadyRegisteredError(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Module already registered: {name}")


class ModuleNotRegisteredError(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Module not registered: {name}")


type RequestType = Literal["command", "query"]


class HandlerAlreadyRegisteredError(ValueError):
    def __init__(self, type: RequestType, name: str) -> None:
        super().__init__(f"Handler already registered for {type}: {name}")


class HandlerNotRegisteredError(ValueError):
    def __init__(self, type: RequestType, name: str) -> None:
        super().__init__(f"Handler not registered for {type}: {name}")


class CommandHandlerAlreadyRegisteredError(HandlerAlreadyRegisteredError):
    def __init__(self, name: str) -> None:
        super().__init__(type="command", name=name)


class CommandHandlerNotRegisteredError(HandlerNotRegisteredError):
    def __init__(self, name: str) -> None:
        super().__init__(type="command", name=name)


class QueryHandlerAlreadyRegisteredError(HandlerAlreadyRegisteredError):
    def __init__(self, name: str) -> None:
        super().__init__(type="query", name=name)


class QueryHandlerNotRegisteredError(HandlerNotRegisteredError):
    def __init__(self, name: str) -> None:
        super().__init__(type="query", name=name)


class DependencyAlreadyRegistered(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Dependency already registered: {name}")


class DependencyNotRegistered(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Dependency not registered: {name}")


class ConcurrencyError(ValueError):
    def __init__(self, aggregate_id: UUID, expected: int, actual: int) -> None:
        super().__init__(
            f"Version mismatch for {aggregate_id}: expected {expected}, actual {actual}"
        )


class AggregateEventHandlerNotRegisteredError(LookupError):
    def __init__(self, name: str) -> None:
        super().__init__(f"No aggregate event handler registered for: {name}")
