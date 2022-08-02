from ansys.fluent.core import examples

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
    flprz_filename = examples.download_file(
        "project-elbow-param.flprz", "pyfluent/mixing_elbow"
    )
    session = ParametricSession(
        project_filepath=flprz_filename,
        launcher=ParametricSessionLauncher(precision="double", processor_count=2),
    )

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
    project.save_as(project_filepath="test.flprj")
    session.exit()

    # Step 5: Repeat 1 and 2
    # Step1: Read flprj or flprz
    # Launch Fluent in 3D and double precision
    session = ParametricSession(
        project_filepath=flprz_filename,
        launcher=ParametricSessionLauncher(precision="double", processor_count=2),
    )

    # Step 2: Get input and output parameters and create a dictionary
    studies = session.studies

    for key in list(studies.keys()):
        study = studies[key]
        if study.is_current:  # save this study
            dp = study.current_design_point  # -> save this dp
            assert dp.input_parameters == {
                "inlet1_vel": 0.5,
                "inlet2_temp": 350.0,
                "inlet1_temp": 300.0,
                "inlet2_vel": 1.0,
            }
            assert dp.output_parameters == {
                "outlet-temp-avg-op": 333.3487,
                "outlet-vel-avg-op": 1.506855,
            }
