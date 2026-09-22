mypy:
	uv run mypy src

test:
	uv run pytest

cov:
	uv run pytest --cov=src --cov-report=term-missing

pc:
	uv run pre-commit run --all-files
