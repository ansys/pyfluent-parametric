from pathlib import Path

import ansys.fluent.core as pyfluent
import pytest

from ansys.fluent.parametric import ParametricStudy


@pytest.mark.integration
@pytest.mark.setup
def test_param_static_mixer(load_static_mixer_parameter):
    session = load_static_mixer_parameter
    session.solver.tui.solve.set.number_of_iterations("100")
    session.solver.tui.solve.monitors.residual.criterion_type("0")
    case_path = str(Path(pyfluent.EXAMPLES_PATH) / "save_1.cas.h5")
    session.solver.tui.file.write_case(case_path)
    assert (Path(pyfluent.EXAMPLES_PATH) / "save_1.cas.h5").exists() == True
    study_1 = ParametricStudy(session.solver.root.parametric_studies).initialize()
    parametric_studies_exp = 1
    parametric_studies_test = len(study_1.get_all_studies().keys())
    assert parametric_studies_test == parametric_studies_exp
    input_parameters_update = study_1.design_points["Base DP"].input_parameters
    input_parameters_update["inlet1_vel"] = 0.5
    study_1.design_points["Base DP"].input_parameters = input_parameters_update
    base_dp_input_expected = {
        "inlet1_vel": 0.5,
        "inlet2_temp": 350.0,
        "inlet2_vel": 1.0,
        "inlet1_temp": 300.0,
    }
    base_dp_input_tested = study_1.design_points["Base DP"].input_parameters
    assert base_dp_input_tested == base_dp_input_expected
    study_1.update_current_design_point()
    assert len(study_1.design_points) == 1
    base_dp_output_expected = {
        "outlet-temp-avg-op": 333.3487,
        "outlet-vel-avg-op": 1.506855,
    }
    base_dp_output_tested = study_1.design_points["Base DP"].output_parameters
    assert base_dp_output_tested == pytest.approx(base_dp_output_expected)
    design_point_1 = study_1.add_design_point()
    design_point_1_input_parameters = study_1.design_points["DP1"].input_parameters
    design_point_1_input_parameters["inlet1_temp"] = 500
    design_point_1_input_parameters["inlet1_vel"] = 1
    design_point_1_input_parameters["inlet2_vel"] = 1
    study_1.design_points["DP1"].input_parameters = design_point_1_input_parameters
    assert len(study_1.design_points) == 2
    dp1_input_expected = {
        "inlet2_vel": 1.0,
        "inlet2_temp": 350.0,
        "inlet1_vel": 1.0,
        "inlet1_temp": 500.0,
    }
    dp1_input_tested = study_1.design_points["DP1"].input_parameters
    assert dp1_input_tested == dp1_input_expected
    design_point_2 = study_1.duplicate_design_point(design_point_1)
    dp2_input_tested = study_1.design_points["DP2"].input_parameters
    assert dp2_input_tested == dp1_input_expected
    assert len(study_1.design_points) == 3
    study_1.update_all_design_points()
    base_dp_output_expected = {
        "outlet-temp-avg-op": 333.3487,
        "outlet-vel-avg-op": 1.506855,
    }
    dp1_output_expected = {"outlet-temp-avg-op": 425.004, "outlet-vel-avg-op": 2.029791}
    dp2_output_expected = {"outlet-temp-avg-op": 425.004, "outlet-vel-avg-op": 2.029791}
    base_dp_output_tested = study_1.design_points["Base DP"].output_parameters
    dp1_output_tested = study_1.design_points["DP1"].output_parameters
    dp2_output_tested = study_1.design_points["DP2"].output_parameters
    assert base_dp_output_tested == pytest.approx(base_dp_output_expected)
    assert dp1_output_tested == pytest.approx(dp1_output_expected)
    assert dp2_output_tested == pytest.approx(dp2_output_expected)
    assert len(study_1.design_points) == 3
    design_point_table = str(
        Path(pyfluent.EXAMPLES_PATH) / "design_point_table_study_1.csv"
    )
    study_1.export_design_table(design_point_table)
    study_1.delete_design_points([design_point_1])
    assert len(study_1.design_points) == 2
    study_2 = study_1.duplicate()
    assert len(study_2.design_points) == 2
    parametric_studies_exp = 2
    parametric_studies_test = len(ParametricStudy._all_studies.keys())
    assert parametric_studies_test == parametric_studies_exp
    study_2.rename("New Study")
    study_1.delete()
    parametric_studies_exp = 1
    parametric_studies_test = len(ParametricStudy._all_studies.keys())
    assert parametric_studies_test == parametric_studies_exp
    project_filepath = str(Path(pyfluent.EXAMPLES_PATH) / "static_mixer_study.flprj")
    session.solver.tui.file.parametric_project.save_as(project_filepath)
    assert (Path(pyfluent.EXAMPLES_PATH) / "static_mixer_study.flprj").exists() == True
    session.exit()
