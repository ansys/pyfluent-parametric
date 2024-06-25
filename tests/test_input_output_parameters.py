import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
import pytest

from ansys.fluent.parametric.parameters import InputParameters, OutputParameters


def test_input_output_parameters(monkeypatch: pytest.MonkeyPatch):
    case_filepath = examples.download_file("nozzle-2D-WB.cas.h5", "pyfluent/optislang")
    solver_session = pyfluent.launch_fluent(version="2d", mode="solver")
    solver_session.file.read_case(file_name=case_filepath)
    inp = InputParameters(solver_session)
    assert len(inp) == 1
    assert inp["inlet_pressure"] == "0.9 [atm]"
    assert inp.get_unit_label("inlet_pressure") == "atm"

    inp["inlet_pressure"] = "0.91 [atm]"
    assert inp["inlet_pressure"] == "0.91 [atm]"
    assert inp.get_unit_label("inlet_pressure") == "atm"

    inp["inlet_pressure"] = 0.92
    assert inp["inlet_pressure"] == "0.92 [atm]"
    assert inp.get_unit_label("inlet_pressure") == "atm"

    inp["inlet_pressure"] = "90000 [Pa]"
    assert inp["inlet_pressure"] == "90000 [Pa]"
    assert inp.get_unit_label("inlet_pressure") == "Pa"

    inp["inlet_pressure"] = 90001
    assert inp["inlet_pressure"] == "90001 [Pa]"
    assert inp.get_unit_label("inlet_pressure") == "Pa"

    inp["inlet_pressure"] = "90002[Pa]"
    assert inp["inlet_pressure"] == "90002[Pa]"
    assert inp.get_unit_label("inlet_pressure") == "Pa"

    inp["inlet_pressure"] = 90003
    assert inp["inlet_pressure"] == "90003 [Pa]"
    assert inp.get_unit_label("inlet_pressure") == "Pa"

    outp = OutputParameters(solver_session)
    assert len(outp) == 1
    assert outp["mass-outlet-op"] == "0.0 [kg/s]"

    solver_session.exit()
