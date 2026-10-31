from types import TracebackType
from typing import Self

from src.app.aggregate import AggregateRoot


class UnitOfWork:
    def __init__(self) -> None:
        self._saved_aggregates: list[AggregateRoot] = []

    async def __aenter__(self) -> Self:
        await self.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
                return
            try:
                await self.commit()
            except BaseException:
                await self.rollback()
                raise
            for aggregate in self._saved_aggregates:
                aggregate.mark_committed()
        finally:
            self._saved_aggregates.clear()

    async def begin(self) -> None:
        raise NotImplementedError

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError

    def mark_saved(self, aggregate: AggregateRoot) -> None:
        if not any(item is aggregate for item in self._saved_aggregates):
            self._saved_aggregates.append(aggregate)
