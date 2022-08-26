import ansys.fluent.core as pyfluent
import pytest


@pytest.fixture
def with_launching_container(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYFLUENT_LAUNCH_CONTAINER", "1")


@pytest.fixture
def new_session(with_launching_container):
    session = pyfluent.launch_fluent(version="2d")
    yield session
    session.exit()
