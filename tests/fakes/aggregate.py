from uuid import UUID

from src.app.aggregate import AggregateRoot


class FakeAggregate(AggregateRoot):
    def __init__(self, aggregate_id: UUID) -> None:
        super().__init__(aggregate_id)
        self.foo = "bar"
