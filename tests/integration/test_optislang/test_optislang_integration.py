import os
from pathlib import Path
import shutil

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
import pytest

from ansys.fluent.parametric import ParametricSession, ParametricSessionLauncher


def test_parametric_project():
    """

    Use Case 3: Parametric Study Test
    ------------------------------

    This optiSLang integration test performs these steps

    - Read flprz
    - Get input and output parameters and create dictionary
    - Set variation
    - Solve
    - Reread project
    - Get input and output parameters

    This test queries the following using PyTest:
    - Input parameters
    - Output parameters
    """

    # Step1: Read flprz
    # Launch Fluent in 3D and double precision
    temporary_resource_path = os.path.join(
        pyfluent.EXAMPLES_PATH, "test_parametric_project_resources"
    )
    if os.path.exists(temporary_resource_path):
        shutil.rmtree(temporary_resource_path, ignore_errors=True)
    if not os.path.exists(temporary_resource_path):
        os.mkdir(temporary_resource_path)
    flprz_filename = examples.download_file(
        "project-elbow-param.flprz", "pyfluent/mixing_elbow"
    )
    session = ParametricSession(
        project_filepath=flprz_filename,
        launcher=ParametricSessionLauncher(precision="double", processor_count=2),
    )

    # Save project
    proj_path = str(Path(temporary_resource_path) / "project-elbow-param.flprj")
    session.project.save_as(project_filepath=proj_path)
    assert (
        Path(temporary_resource_path) / "project-elbow-param.flprj"
    ).exists() == True

    # Step 2: Get input and output parameters and create a dictionary
    studies = session.studies
    for key in list(studies.keys()):
        study = studies[key]
        if study.is_current:  # save this study
            dp = study.current_design_point  # -> save this dp
            dp.input_parameters
            dp.output_parameters

    # Step 3: Set variation – this would again have an input dictionary that is
    # same as the one obtained in Step 2
    study.clear_generated_data([dp])
    dp.input_parameters = {
        "inlet2_vel": 2.0,
        "inlet1_vel": 1.5,
        "inlet2_temp": 400.0,
        "inlet1_temp": 350.0,
    }
    project = session.project
    project.save()

    # Step 4: Solve
    study.update_selected_design_points([dp])
    project.save()

    for key in list(studies.keys()):
        study = studies[key]
        if study.is_current:  # save this study
            dp = study.current_design_point  # -> save this dp
            assert dp.input_parameters == {
                "inlet2_vel": 2.0,
                "inlet1_vel": 1.5,
                "inlet2_temp": 400.0,
                "inlet1_temp": 350.0,
            }
            assert pytest.approx(dp.output_parameters["outlet-temp-avg-op"]) == 378.5117
            assert pytest.approx(dp.output_parameters["outlet-vel-avg-op"]) == 3.69182

    # Save and exit
    project.save()
    session.exit()
    shutil.rmtree(temporary_resource_path, ignore_errors=True)


def test_optislang_integration_doe_1ip():
    ############################################################################
    # Launch Fluent in 3D and double precision
    solver = pyfluent.launch_fluent(
        precision="double", processor_count=4, mode="solver"
    )
    assert solver.check_health() == "SERVING"

    # Avoid running for versions older than 23.1
    if float(solver.get_fluent_version()[:-2]) > 22.2:
        ############################################################################
        # Create a directory structure to store the temporarily created files in
        # this test.
        temporary_resource_path = os.path.join(
            pyfluent.EXAMPLES_PATH, "parametric_optislang_doe_resources"
        )
        if os.path.exists(temporary_resource_path):
            shutil.rmtree(temporary_resource_path, ignore_errors=True)
        if not os.path.exists(temporary_resource_path):
            os.mkdir(temporary_resource_path)

        ############################################################################
        # Read the catalytic converter case
        import_filename = examples.download_file(
            "catalytic_converter_param.cas", "pyfluent/catalytic_converter"
        )
        case_path = str(Path(pyfluent.EXAMPLES_PATH) / "catalytic_converter_param.cas")
        solver.tui.file.read_case(case_path)

        ############################################################################
        # Set number of iterations to 50
        solver.solution.run_calculation.iter_count = 50

        ###########################################################################
        # Instantiate a parametric study from a Fluent session
        project_filepath = str(
            Path(temporary_resource_path) / "catalytic_converter.flprj"
        )
        study_1 = solver.tui.parametric_study.study.initialize("yes", project_filepath)
        assert (
            Path(temporary_resource_path) / "catalytic_converter.flprj"
        ).exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "1 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(Path(temporary_resource_path) / "Koshal_Linear1.csv")
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (Path(temporary_resource_path) / "Koshal_Linear1.csv").exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "2 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(
            Path(temporary_resource_path) / "Koshal_quadratic1.csv"
        )
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (
            Path(temporary_resource_path) / "Koshal_quadratic1.csv"
        ).exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "3 2 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(Path(temporary_resource_path) / "Full_Factorial1.csv")
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (Path(temporary_resource_path) / "Full_Factorial1.csv").exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "4 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(
            Path(temporary_resource_path) / "Full_combinatorial1.csv"
        )
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (
            Path(temporary_resource_path) / "Full_combinatorial1.csv"
        ).exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "7 2 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(Path(temporary_resource_path) / "Star_Points1.csv")
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (Path(temporary_resource_path) / "Star_Points1.csv").exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "8 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(
            Path(temporary_resource_path) / "D_optimal_linear1.csv"
        )
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (
            Path(temporary_resource_path) / "D_optimal_linear1.csv"
        ).exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "9 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(
            Path(temporary_resource_path) / "D_optimal_quadratic1.csv"
        )
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (
            Path(temporary_resource_path) / "D_optimal_quadratic1.csv"
        ).exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "10 50 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(
            Path(temporary_resource_path) / "D_optimal_custom1.csv"
        )
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (
            Path(temporary_resource_path) / "D_optimal_custom1.csv"
        ).exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "11 50 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(
            Path(temporary_resource_path) / "Plain_Monte_Carlo1.csv"
        )
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (
            Path(temporary_resource_path) / "Plain_Monte_Carlo1.csv"
        ).exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "12 100 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(
            Path(temporary_resource_path) / "Latin_Hypercube_Sampling1.csv"
        )
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (
            Path(temporary_resource_path) / "Latin_Hypercube_Sampling1.csv"
        ).exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "13 100 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(
            Path(temporary_resource_path) / "Advanced_Latin_Hypercube_Sampling1.csv"
        )
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (
            Path(temporary_resource_path) / "Advanced_Latin_Hypercube_Sampling1.csv"
        ).exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "14 100 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(
            Path(temporary_resource_path) / "Space_filling_Latin_Hypercube1.csv"
        )
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (
            Path(temporary_resource_path) / "Space_filling_Latin_Hypercube1.csv"
        ).exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "15 200 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()
        design_point_table = str(Path(temporary_resource_path) / "Sobol_Sequence1.csv")
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (Path(temporary_resource_path) / "Sobol_Sequence1.csv").exists() == True

        ###########################################################################
        # Auto-create design points with optislang and export design tables
        solver.tui.parametric_study.design_points.auto_create.create_design_points(
            "13 10 10 40 yes"
        )
        solver.tui.parametric_study.design_points.auto_create.list_current_settings()

        ###########################################################################
        # Capture simulation report data
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            '"Base DP"', "no"
        )
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            "DP1 no"
        )
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            "DP2 no"
        )
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            "DP3 no"
        )
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            "DP4 no"
        )
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            "DP5 no"
        )
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            "DP6 no"
        )
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            "DP7 no"
        )
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            "DP8 no"
        )
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            "DP9 no"
        )
        solver.tui.parametric_study.design_points.set.capture_simulation_report_data(
            "DP10 no"
        )

        ###########################################################################
        # Update all design points and export updated design table
        solver.tui.parametric_study.update.update_all()
        design_point_table = str(Path(temporary_resource_path) / "dp_table1.csv")
        solver.tui.parametric_study.design_points.table.export_design_table(
            design_point_table
        )
        assert (Path(temporary_resource_path) / "dp_table1.csv").exists() == True

        ###########################################################################
        # Save the project and exit
        solver.tui.file.parametric_project.save()
        assert (
            Path(temporary_resource_path) / "catalytic_converter.flprj"
        ).exists() == True
        solver.exit()
        shutil.rmtree(temporary_resource_path, ignore_errors=True)
