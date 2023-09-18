import functools
import operator

from ansys.fluent.core.launcher.launcher import FluentVersion
from packaging.version import Version
import pytest

_fluent_versions = list(FluentVersion)
_fluent_release_version = _fluent_versions[1]


def pytest_addoption(parser):
    parser.addoption(
        "--fluent-version",
        action="store",
        metavar="VERSION",
        help="only run tests supported by Fluent version VERSION.",
    )
    parser.addoption(
        "--self-hosted",
        action="store_true",
        default=False,
        help="only run tests that require self-hosted runners",
    )


def pytest_runtest_setup(item):
    version_specs = []
    if version_specs:
        combined_spec = functools.reduce(operator.and_, version_specs)
        version = item.config.getoption("--fluent-version")
        if version and Version(version) not in combined_spec:
            pytest.skip()

    self_hosted = item.config.getoption("--self-hosted")
    if not self_hosted and any(
        mark.name == "self_hosted" for mark in item.iter_markers()
    ):
        pytest.skip()

    if self_hosted and not any(
        mark.name == "self_hosted" for mark in item.iter_markers()
    ):
        pytest.skip()


@pytest.fixture(autouse=True)
def run_before_each_test(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> None:
    monkeypatch.setenv("PYFLUENT_TEST_NAME", request.node.name)
