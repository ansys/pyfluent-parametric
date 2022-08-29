"""
This parametric study workflow test performs these steps

- Reads a case file and data file
- Creates input and output parameters
- Instantiates a design point study
- Accesses and modifies the input parameters of
  the base design point (DP)
- Updates design points
- Creates, updates, and deletes more DPs
- Creates, renames, duplicates and deletes parametric studies

This test queries the following using PyTest:
- Input parameters
- Output parameters
- Number of design points after creation, duplication and deletion
"""

############################################################################
from pathlib import Path

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
import pytest

from ansys.fluent.parametric import ParametricProject, ParametricStudy


def test_parametric_workflow():
    ############################################################################
    # Launch Fluent in 3D and double precision

    solver_session = pyfluent.launch_fluent(
        precision="double", processor_count=2, start_transcript=False, mode="solver"
    )

    ############################################################################
    # Read the hopper/mixer case

    import_filename = examples.download_file(
        "Static_Mixer_main.cas.h5", "pyfluent/static_mixer"
    )

    solver_session.tui.file.read_case(case_file_name=import_filename)

    ############################################################################
    # Set number of iterations to 100
    solver_session.tui.solve.set.number_of_iterations("100")

    ############################################################################
    # Create input parameters after enabling parameter creation in the TUI:
    # Parameter values:
    # Inlet1: velocity (inlet1_vel) 0.5 m/s and temperature (inlet1_temp) at 300 K
    # Inlet2: velocity (inlet2_vel) 0.5 m/s and temperature (inlet2_temp) at 350 K

    solver_session.tui.define.parameters.enable_in_TUI("yes")

    solver_session.tui.define.boundary_conditions.set.velocity_inlet(
        "inlet1", (), "vmag", "yes", "inlet1_vel", 1, "quit"
    )
    solver_session.tui.define.boundary_conditions.set.velocity_inlet(
        "inlet1", (), "temperature", "yes", "inlet1_temp", 300, "quit"
    )
    solver_session.tui.define.boundary_conditions.set.velocity_inlet(
        "inlet2", (), "vmag", "yes", "no", "inlet2_vel", 1, "quit"
    )
    solver_session.tui.define.boundary_conditions.set.velocity_inlet(
        "inlet2", (), "temperature", "yes", "no", "inlet2_temp", 350, "quit"
    )

    ###########################################################################
    # Create output parameters using report definitions
    # TODO: Remove the if condition after a stable version of 23.1 is available
    #  and update the commands as required.
    if float(solver_session.get_fluent_version()[:-2]) < 23.0:

        solver_session.solution.report_definitions.surface["outlet-temp-avg"] = {}
        print(solver_session.solution.report_definitions())
        solver_session.solution.report_definitions.surface[
            "outlet-temp-avg"
        ].report_type = "surface-areaavg"
        solver_session.solution.report_definitions.surface[
            "outlet-temp-avg"
        ].field = "temperature"
        solver_session.solution.report_definitions.surface[
            "outlet-temp-avg"
        ].surface_names = ["outlet"]

        solver_session.solution.report_definitions.surface["outlet-vel-avg"] = {}
        solver_session.solution.report_definitions.surface[
            "outlet-vel-avg"
        ].report_type = "surface-areaavg"
        solver_session.solution.report_definitions.surface[
            "outlet-vel-avg"
        ].field = "velocity-magnitude"
        solver_session.solution.report_definitions.surface[
            "outlet-vel-avg"
        ].surface_names = ["outlet"]

    solver_session.tui.define.parameters.enable_in_TUI("yes")
    solver_session.tui.define.parameters.output_parameters.create(
        "report-definition", "outlet-temp-avg"
    )
    solver_session.tui.define.parameters.output_parameters.create(
        "report-definition", "outlet-vel-avg"
    )

    ###########################################################################
    # Enable convergence condition check

    solver_session.tui.solve.monitors.residual.criterion_type("0")

    ###########################################################################
    # Write case with all the settings in place
    case_path = str(Path(pyfluent.EXAMPLES_PATH) / "Static_Mixer_Parameters.cas.h5")
    solver_session.tui.file.write_case(case_path)

    assert (
        Path(pyfluent.EXAMPLES_PATH) / "Static_Mixer_Parameters.cas.h5"
    ).exists() == True

    ###########################################################################
    # Instantiate a parametric study from a Fluent session

    study_1 = ParametricStudy(solver_session.parametric_studies).initialize()

    parametricStudies_exp = 1
    parametricStudies_test = len(study_1.get_all_studies().keys())
    assert parametricStudies_test == parametricStudies_exp

    ###########################################################################
    # Access and modify input parameters of base DP

    input_parameters_update = study_1.design_points["Base DP"].input_parameters
    input_parameters_update["inlet1_vel"] = 0.5
    study_1.design_points["Base DP"].input_parameters = input_parameters_update

    ###########################################################################
    # Validate input parameters of base design point

    base_DP_input_expected = {
        "inlet1_vel": 0.5,
        "inlet2_temp": 350.0,
        "inlet2_vel": 1.0,
        "inlet1_temp": 300.0,
    }
    base_DP_input_tested = study_1.design_points["Base DP"].input_parameters

    assert base_DP_input_tested == base_DP_input_expected

    ###########################################################################
    # Update current design point

    study_1.update_current_design_point()

    ###########################################################################
    # Validate Base DP output parameters

    assert len(study_1.design_points) == 1
    base_DP_output_expected = {
        "outlet-temp-avg-op": 333.3487,
        "outlet-vel-avg-op": 1.506855,
    }
    base_DP_output_tested = study_1.design_points["Base DP"].output_parameters

    assert base_DP_output_tested == pytest.approx(base_DP_output_expected)

    ###########################################################################
    # Add a new design point

    design_point_1 = study_1.add_design_point()
    design_point_1_input_parameters = study_1.design_points["DP1"].input_parameters
    design_point_1_input_parameters["inlet1_temp"] = 500
    design_point_1_input_parameters["inlet1_vel"] = 1
    design_point_1_input_parameters["inlet2_vel"] = 1
    study_1.design_points["DP1"].input_parameters = design_point_1_input_parameters

    ###########################################################################
    # Validate new design points

    assert len(study_1.design_points) == 2
    DP1_input_expected = {
        "inlet2_vel": 1.0,
        "inlet2_temp": 350.0,
        "inlet1_vel": 1.0,
        "inlet1_temp": 500.0,
    }
    DP1_input_tested = study_1.design_points["DP1"].input_parameters
    assert DP1_input_tested == DP1_input_expected

    ##########################################################################
    # Duplicate design points

    design_point_2 = study_1.duplicate_design_point(design_point_1)

    ###########################################################################
    # Validate duplicated design points

    DP2_input_tested = study_1.design_points["DP2"].input_parameters
    assert DP2_input_tested == DP1_input_expected

    assert len(study_1.design_points) == 3

    #########################################################################
    # Update all design points for study 1

    study_1.update_all_design_points()

    ###########################################################################
    # Validate all output design points

    BaseDP_output_expected = {
        "outlet-temp-avg-op": 333.3487,
        "outlet-vel-avg-op": 1.506855,
    }
    DP1_output_expected = {"outlet-temp-avg-op": 425.004, "outlet-vel-avg-op": 2.029791}
    DP2_output_expected = {"outlet-temp-avg-op": 425.004, "outlet-vel-avg-op": 2.029791}

    BaseDP_output_tested = study_1.design_points["Base DP"].output_parameters
    DP1_output_tested = study_1.design_points["DP1"].output_parameters
    DP2_output_tested = study_1.design_points["DP2"].output_parameters

    assert BaseDP_output_tested == pytest.approx(BaseDP_output_expected)
    assert DP1_output_tested == pytest.approx(DP1_output_expected)
    assert DP2_output_tested == pytest.approx(DP2_output_expected)
    assert len(study_1.design_points) == 3

    ###############################################################################
    # Export design point table as a CSV table

    design_point_table = str(
        Path(pyfluent.EXAMPLES_PATH) / "design_point_table_study_1.csv"
    )
    study_1.export_design_table(design_point_table)

    ##########################################################################
    # Delete design points

    study_1.delete_design_points([design_point_1])
    assert len(study_1.design_points) == 2

    ##########################################################################
    # Create a new parametric study by duplicating the current one

    study_2 = study_1.duplicate()
    assert len(study_2.design_points) == 2

    parametricStudies_exp = 2
    parametricStudies_test = len(study_1.get_all_studies().keys())
    assert parametricStudies_test == parametricStudies_exp

    #########################################################################
    # Rename the newly created parametric study

    study_2.rename("New Study")

    #########################################################################
    # Delete the old parametric study

    study_1.delete()

    parametricStudies_exp = 1
    parametricStudies_test = len(study_1.get_all_studies().keys())
    assert parametricStudies_test == parametricStudies_exp

    #########################################################################
    # Save the parametric project and close Fluent

    project_filepath = str(Path(pyfluent.EXAMPLES_PATH) / "static_mixer_study.flprj")

    solver_session.tui.file.parametric_project.save_as(project_filepath)

    assert (Path(pyfluent.EXAMPLES_PATH) / "static_mixer_study.flprj").exists() == True

    solver_session.exit()

    #########################################################################
    # Launch Fluent again and read the previously saved project

    solver_session = pyfluent.launch_fluent(
        precision="double", processor_count=2, mode="solver"
    )
    project_filepath_read = str(
        Path(pyfluent.EXAMPLES_PATH) / "static_mixer_study.flprj"
    )

    proj = ParametricProject(
        solver_session.file.parametric_project,
        solver_session.parametric_studies,
        project_filepath_read,
    )

    #########################################################################
    # Save the current project

    proj.save()

    #########################################################################
    # Save the current project to a different file name

    project_filepath_save_as = str(
        Path(pyfluent.EXAMPLES_PATH) / "static_mixer_study_save_as.flprj"
    )
    proj.save_as(project_filepath=project_filepath_save_as)

    assert (
        Path(pyfluent.EXAMPLES_PATH) / "static_mixer_study_save_as.flprj"
    ).exists() == True

    #########################################################################
    # Export the current project

    project_filepath_export = str(
        Path(pyfluent.EXAMPLES_PATH) / "static_mixer_study_export.flprj"
    )
    proj.export(project_filepath=project_filepath_export)

    assert (
        Path(pyfluent.EXAMPLES_PATH) / "static_mixer_study_export.flprj"
    ).exists() == True

    #########################################################################
    # Archive the current project

    proj.archive()

    assert (Path(pyfluent.EXAMPLES_PATH) / "static_mixer_study.flprz").exists() == True

    #########################################################################
    # Close Fluent

    solver_session.exit()
