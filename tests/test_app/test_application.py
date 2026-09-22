import pytest

from src.app.application import Application
from src.app.errors import ModuleAlreadyRegisteredError, ModuleNotRegisteredError
from src.app.module import Module


def test_application_adds_module():
    app = Application()
    module = Module(name="test")

    app.add(module)

    assert module in app.modules


def test_application_raises_for_added_module():
    app = Application()
    module = Module(name="test")

    app.add(module)

    with pytest.raises(ModuleAlreadyRegisteredError, match=rf"already registered: {module.name}"):
        app.add(module)


def test_application_raises_for_missing_module():
    app = Application()
    module = Module(name="test")

    with pytest.raises(ModuleNotRegisteredError, match=rf"not registered: {module.name}"):
        app.get(module.name)
