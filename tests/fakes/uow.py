from src.app.uow import UnitOfWork


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, fail_commit=False) -> None:
        super().__init__()
        self.began = False
        self.committed = False
        self.rolled_back = False
        self.fail_commit = fail_commit

    async def begin(self) -> None:
        self.began = True

    async def commit(self) -> None:
        if self.fail_commit:
            raise RuntimeError("Commit failed")
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
