"""
This local parametric study workflow test performs these steps

- TODO
"""

############################################################################
from pathlib import Path

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

from ansys.fluent.parametric.local import LocalParametricStudy


def test_parametric_local():

    session = pyfluent.launch_fluent()

    import_filename = examples.download_file(
        "Static_Mixer_main.cas.h5", "pyfluent/static_mixer"
    )

    session.solver.tui.file.read_case(case_file_name=import_filename)

    session.solver.tui.define.parameters.enable_in_TUI("yes")

    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "inlet1", (), "vmag", "yes", "inlet1_vel", 1, "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "inlet1", (), "temperature", "yes", "inlet1_temp", 300, "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "inlet2", (), "vmag", "yes", "no", "inlet2_vel", 1, "quit"
    )
    session.solver.tui.define.boundary_conditions.set.velocity_inlet(
        "inlet2", (), "temperature", "yes", "no", "inlet2_temp", 350, "quit"
    )

    session.solver.root.solution.report_definitions.surface["outlet-temp-avg"] = {}
    session.solver.root.solution.report_definitions.surface[
        "outlet-temp-avg"
    ].report_type = "surface-areaavg"
    session.solver.root.solution.report_definitions.surface[
        "outlet-temp-avg"
    ].field = "temperature"
    session.solver.root.solution.report_definitions.surface[
        "outlet-temp-avg"
    ].surface_names = ["outlet"]

    session.solver.root.solution.report_definitions.surface["outlet-vel-avg"] = {}
    session.solver.root.solution.report_definitions.surface[
        "outlet-vel-avg"
    ].report_type = "surface-areaavg"
    session.solver.root.solution.report_definitions.surface[
        "outlet-vel-avg"
    ].field = "velocity-magnitude"
    session.solver.root.solution.report_definitions.surface[
        "outlet-vel-avg"
    ].surface_names = ["outlet"]

    session.solver.tui.define.parameters.enable_in_TUI("yes")
    session.solver.tui.define.parameters.output_parameters.create(
        "report-definition", "outlet-temp-avg"
    )
    session.solver.tui.define.parameters.output_parameters.create(
        "report-definition", "outlet-vel-avg"
    )

    param_case_path = str(
        Path(pyfluent.EXAMPLES_PATH) / "Static_Mixer_Parameters.cas.h5"
    )
    session.solver.tui.file.write_case(param_case_path)

    local_study = LocalParametricStudy(case_filepath=param_case_path)

    base_design_point = local_study.design_point("Base DP")

    input_parameters = base_design_point.input_parameters

    assert len(input_parameters)

    output_parameters = base_design_point.output_parameters

    assert len(output_parameters)

    print(input_parameters)
    print(output_parameters)
