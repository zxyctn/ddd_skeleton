from src.app.module import Module


class Application:
    def __init__(self) -> None:
        self._modules: dict[str, Module] = {}

    def add(self, module: Module) -> None:
        if module.name in self._modules:
            raise ValueError(f"Module already registered: {module.name}")

        self._modules[module.name] = module

    def get(self, name: str) -> Module:
        return self._modules[name]

    @property
    def modules(self) -> tuple[Module, ...]:
        return tuple(self._modules.values())
