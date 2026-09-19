from typing import Literal


class ModuleAlreadyRegisteredError(ValueError):
    def __init__(self, *args: object, name: str) -> None:
        super().__init__(*args)
        self.add_note(f"Module already registered: {name}")


class ModuleNotRegisteredError(ValueError):
    def __init__(self, *args: object, name: str) -> None:
        super().__init__(*args)
        self.add_note(f"Module not registered: {name}")


type RequestType = Literal["command", "query"]


class HandlerAlreadyRegisteredError(ValueError):
    def __init__(self, *args: object, type: RequestType, name: str) -> None:
        super().__init__(*args)
        self.add_note(f"Handler already registered for {type}: {name}")


class HandlerNotRegisteredError(ValueError):
    def __init__(self, *args: object, type: RequestType, name: str) -> None:
        super().__init__(*args)
        self.add_note(f"Handler not registered for {type}: {name}")


class CommandHandlerAlreadyRegisteredError(HandlerAlreadyRegisteredError):
    def __init__(self, *args: object, name: str, type: RequestType = "command") -> None:
        super().__init__(*args, type=type, name=name)


class CommandHandlerNotRegisteredError(HandlerNotRegisteredError):
    def __init__(self, *args: object, name: str, type: RequestType = "command") -> None:
        super().__init__(*args, type=type, name=name)


class QueryHandlerAlreadyRegisteredError(HandlerAlreadyRegisteredError):
    def __init__(self, *args: object, name: str, type: RequestType = "query") -> None:
        super().__init__(*args, type=type, name=name)


class QueryHandlerNotRegisteredError(HandlerNotRegisteredError):
    def __init__(self, *args: object, name: str, type: RequestType = "query") -> None:
        super().__init__(*args, type=type, name=name)
