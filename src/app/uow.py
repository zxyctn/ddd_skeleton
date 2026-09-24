from types import TracebackType
from typing import Self


class UnitOfWork:
    async def __aenter__(self) -> Self:
        await self.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    async def begin(self) -> None:
        raise NotImplementedError

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError
