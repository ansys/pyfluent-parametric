import functools
import operator

import ansys.fluent.core as pyfluent
from packaging.specifiers import SpecifierSet
from packaging.version import Version
import pytest


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
    for mark in item.iter_markers(name="fluent_version"):
        version_specs.append(SpecifierSet(mark.args[0]))
    if version_specs:
        combined_spec = functools.reduce(operator.and_, version_specs)
        run_version = item.config.getoption("--fluent-version")
        if run_version and Version(run_version) not in combined_spec:
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
    monkeypatch.setenv("PYFLUENT_CONTAINER_MOUNT_PATH", pyfluent.EXAMPLES_PATH)
