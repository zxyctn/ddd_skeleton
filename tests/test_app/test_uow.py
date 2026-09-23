import pytest

from src.app.uow import UnitOfWork


@pytest.fixture
def module(module, uow):
    module.provide(UnitOfWork, lambda: uow)
    return module


async def test_uow_commits(uow, module, command, handler):
    module.on_command(command)(handler)
    await module.handle_command(command, data="test")
    assert uow.began is True
    assert uow.committed is True
    assert uow.rolled_back is False


async def test_uow_rolls_back_when_handler_fails(uow, module, command):
    @module.on_command(command)
    async def handler(data):
        raise Exception("test")

    with pytest.raises(Exception, match="test"):
        await module.handle_command(command, data="test")

    assert uow.began is True
    assert uow.committed is False
    assert uow.rolled_back is True
