from typing import Iterator
import pytest

from dotman.context import Context, managed_context


@pytest.fixture
def context_fixture() -> Iterator[Context]:
    with managed_context() as context:
        yield context
