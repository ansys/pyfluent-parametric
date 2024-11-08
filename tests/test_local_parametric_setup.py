"""
This local parametric study workflow test performs these steps

TODO
"""

from ansys.fluent.core import examples
import pytest

from ansys.fluent.parametric.local import LocalParametricStudy

############################################################################


def test_local_parametric_setup(monkeypatch: pytest.MonkeyPatch):
    ############################################################################
    # Read the hopper/mixer case

    case_filepath = examples.download_file(
        "Static_Mixer_Parameters.cas.h5",
        "pyfluent/static_mixer",
        return_without_path=False,
    )

    local_study = LocalParametricStudy(case_filepath=case_filepath)

    base_design_point = local_study.design_point("Base DP")

    input_parameters = base_design_point.input_parameters

    assert len(input_parameters) == 4

    assert input_parameters["inlet1_temp"] == "300 [K]"

    assert input_parameters["inlet1_vel"] == "1 [m/s]"

    assert input_parameters["inlet2_temp"] == "350 [K]"

    assert input_parameters["inlet2_vel"] == "1 [m/s]"

    output_parameters = base_design_point.output_parameters

    assert len(output_parameters) == 2

    assert output_parameters["outlet-temp-avg-op"] == None

    assert output_parameters["outlet-vel-avg-op"] == None
