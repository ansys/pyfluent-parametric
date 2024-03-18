import pytest

PYTEST_RELATIVE_TOLERANCE = 1e-3


def pytest_approx(expected):
    return pytest.approx(expected=expected, rel=PYTEST_RELATIVE_TOLERANCE)
