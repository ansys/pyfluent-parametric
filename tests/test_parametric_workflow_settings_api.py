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
import os
from pathlib import Path
import shutil

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
import pytest

from ansys.fluent.parametric import ParametricProject, ParametricStudy


@pytest.mark.self_hosted
# test not working correctly on GitHub runners, see issue #121
# method that fails: .file.parametric_project.save_as
@pytest.mark.fluent_version(">=24.1")
def test_parametric_workflow_settings_api(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PYFLUENT_CONTAINER_MOUNT_PATH", pyfluent.EXAMPLES_PATH)
    ############################################################################
    # Launch Fluent in 3D and double precision

    solver_session = pyfluent.launch_fluent(
        precision="double",
        processor_count=2,
        start_transcript=False,
        mode="solver",
    )

    ############################################################################
    # Create a directory structure to store the temporarily created files in this test.

    temporary_resource_path = os.path.join(
        pyfluent.EXAMPLES_PATH, "parametric_workflow_resources"
    )
    if os.path.exists(temporary_resource_path):
        shutil.rmtree(temporary_resource_path, ignore_errors=True)
    if not os.path.exists(temporary_resource_path):
        os.mkdir(temporary_resource_path)

    ############################################################################
    # Read the hopper/mixer case

    import_filepath = examples.download_file(
        "Static_Mixer_main.cas.h5", "pyfluent/static_mixer", return_without_path=False
    )

    solver_session.file.read_case(file_name=import_filepath)

    ############################################################################
    # Set number of iterations to 100

    solver_session.solution.run_calculation.iter_count = 100

    ############################################################################
    # Create input parameters
    # Parameter values:
    # Inlet1: velocity (inlet1_vel) 1 m/s and temperature (inlet1_temp) at 300 K
    # Inlet2: velocity (inlet2_vel) 1 m/s and temperature (inlet2_temp) at 350 K

    expressions = solver_session.setup.named_expressions
    velocity_inlet = solver_session.setup.boundary_conditions.velocity_inlet

    expressions["inlet1_vel"] = {
        "input_parameter": True,
        "definition": "1 [m/s]",
        "name": "inlet1_vel",
    }
    expressions["inlet1_temp"] = {
        "input_parameter": True,
        "definition": "300 [K]",
        "name": "inlet1_temp",
    }
    velocity_inlet["inlet1"] = {
        "momentum": {"velocity": {"value": "inlet1_vel"}},
        "thermal": {"t": {"value": "inlet1_temp"}},
    }
    expressions["inlet2_vel"] = {
        "input_parameter": True,
        "definition": "1 [m/s]",
        "name": "inlet2_vel",
    }
    expressions["inlet2_temp"] = {
        "input_parameter": True,
        "definition": "350 [K]",
        "name": "inlet2_temp",
    }
    velocity_inlet["inlet2"] = {
        "momentum": {"velocity": {"value": "inlet2_vel"}},
        "thermal": {"t": {"value": "inlet2_temp"}},
    }

    ###########################################################################
    # Create output parameters using report definitions

    surface = solver_session.solution.report_definitions.surface
    surface["outlet-temp-avg"] = {
        "report_type": "surface-areaavg",
        "field": "temperature",
        "surface_names": "outlet",
    }
    surface["outlet-vel-avg"] = {
        "report_type": "surface-areaavg",
        "field": "velocity-magnitude",
        "surface_names": "outlet",
    }

    report_definitions = solver_session.parameters.output_parameters.report_definitions
    report_definitions["report-def-1"] = {"report_definition": "outlet-temp-avg"}
    report_definitions["report-def-2"] = {"report_definition": "outlet-vel-avg"}

    ###########################################################################
    # Enable convergence condition check

    solver_session.solution.monitor.residual.options.criterion_type = "absolute"

    ###########################################################################
    # Write case with all the settings in place

    case_path = str(Path(temporary_resource_path) / "Static_Mixer_Parameters.cas.h5")
    solver_session.file.write(file_type="case", file_name=case_path)

    assert (Path(temporary_resource_path) / "Static_Mixer_Parameters.cas.h5").exists()

    ###########################################################################
    # Instantiate a parametric study from a Fluent session

    study_1 = ParametricStudy(solver_session.parametric_studies)

    # remove registered studies from previous parametric runs in the current interpreter
    study_1.reset_study_registry()

    assert len(study_1.get_all_studies().keys()) == 1

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

    ###########################################################################
    # Set current design point to DP2

    assert study_1.current_design_point.name == "Base DP"

    study_1.design_points["DP2"].set_as_current()
    assert study_1.current_design_point.name == "DP2"

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
        Path(temporary_resource_path) / "design_point_table_study_1.csv"
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

    assert len(study_1.get_all_studies().keys()) == 2

    #########################################################################
    # Rename the newly created parametric study

    study_2.rename("New Study")

    #########################################################################
    # Delete the old parametric study

    study_1.delete()

    assert len(study_1.get_all_studies().keys()) == 1

    #########################################################################
    # Save the parametric project and close Fluent

    project_filepath = str(Path(temporary_resource_path) / "static_mixer_study.flprj")

    solver_session.file.parametric_project.save_as(project_filename=project_filepath)

    assert (Path(temporary_resource_path) / "static_mixer_study.flprj").exists()

    solver_session.exit()

    #########################################################################
    # Launch Fluent again and read the previously saved project

    solver_session = pyfluent.launch_fluent(
        precision="double", processor_count=2, mode="solver"
    )
    project_filepath_read = str(
        Path(temporary_resource_path) / "static_mixer_study.flprj"
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
        Path(temporary_resource_path) / "static_mixer_study_save_as.flprj"
    )
    proj.save_as(project_filepath=project_filepath_save_as)

    assert (Path(temporary_resource_path) / "static_mixer_study_save_as.flprj").exists()

    #########################################################################
    # Export the current project

    project_filepath_export = str(
        Path(temporary_resource_path) / "static_mixer_study_export.flprj"
    )
    proj.export(project_filepath=project_filepath_export)

    assert (Path(temporary_resource_path) / "static_mixer_study_export.flprj").exists()

    #########################################################################
    # Archive the current project

    proj.archive()

    assert (Path(temporary_resource_path) / "static_mixer_study.flprz").exists()

    #########################################################################
    # Close Fluent

    solver_session.exit()
    shutil.rmtree(temporary_resource_path, ignore_errors=True)
