from src.app.errors import ModuleAlreadyRegisteredError, ModuleNotRegisteredError
from src.app.module import Module


class Application:
    def __init__(self) -> None:
        self._modules: dict[str, Module] = {}

    def add(self, module: Module) -> None:
        if module.name in self._modules:
            raise ModuleAlreadyRegisteredError(name=module.name)

        self._modules[module.name] = module

    def get(self, name: str) -> Module:
        if name not in self._modules:
            raise ModuleNotRegisteredError(name=name)
        return self._modules[name]

    @property
    def modules(self) -> tuple[Module, ...]:
        return tuple(self._modules.values())
