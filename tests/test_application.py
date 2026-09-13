from src.app.application import Application
from src.app.module import Module


def test_application_adds_module():
    app = Application()
    module = Module(name="test")

    app.add(module)

    assert module in app.modules
