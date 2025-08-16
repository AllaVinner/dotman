uv run ruff check --fix
uv run ruff format
uv run mypy src/dotman --check-untyped-defs
uv run mypy tests  --check-untyped-defs
uv run pytest
