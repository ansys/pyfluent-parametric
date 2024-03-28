import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
import pytest

from ansys.fluent.parametric import ParametricSession


def test_parametric_session(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PYFLUENT_CONTAINER_MOUNT_PATH", pyfluent.EXAMPLES_PATH)
    project_filepath = examples.download_file(
        "project-elbow-param.flprz",
        "pyfluent/mixing_elbow",
        return_without_path=False,
    )
    session = ParametricSession(project_filepath=project_filepath, initialize=False)
    assert "Static_Mixer_main-Solve" in session.studies
    design_points = session.studies["Static_Mixer_main-Solve"].design_points
    assert "Base DP" in design_points
    assert "DP1" in design_points
    assert "DP2" in design_points
