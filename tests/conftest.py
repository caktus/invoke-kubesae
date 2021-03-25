from unittest import mock
import pytest
from invoke.context import Context


@pytest.fixture
def c():
    context = Context()
    context.run = mock.Mock()
    return context
