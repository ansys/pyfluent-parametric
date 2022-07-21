"""
This local parametric study workflow test performs these steps

TODO
"""

############################################################################

from ansys.fluent.core import examples

from ansys.fluent.parametric.local import LocalParametricStudy


def test_parametric_local():

    ############################################################################
    # Read the hopper/mixer case

    case_filename = examples.download_file(
        "Static_Mixer_Parameters.cas.h5", "pyfluent/static_mixer"
    )

    local_study = LocalParametricStudy(case_filepath=case_filename)

    base_design_point = local_study.design_point("Base DP")

    input_parameters = base_design_point.input_parameters

    assert len(input_parameters)

    output_parameters = base_design_point.output_parameters

    assert len(output_parameters)
