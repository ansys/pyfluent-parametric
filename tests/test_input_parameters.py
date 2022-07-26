import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
import pytest

from ansys.fluent.parametric.parameters import InputParameters


def test_input_parameters():
    case_filepath = examples.download_file("nozzle-2D-WB.cas.h5", "pyfluent/optislang")
    session = pyfluent.launch_fluent(version="2d")
    session.solver.root.file.read(file_name=case_filepath, file_type="case")
    inp = InputParameters(session)
    assert len(inp) == 1
    assert inp["inlet_pressure"] == "91192.5 [atm]"
    assert inp.get_unit_label("inlet_pressure") == "atm"

    inp["inlet_pressure"] = "90000 [atm]"
    assert inp["inlet_pressure"] == "90000.0 [atm]"
    assert inp.get_unit_label("inlet_pressure") == "atm"

    inp["inlet_pressure"] = 90005
    assert inp["inlet_pressure"] == "90005.0 [atm]"
    assert inp.get_unit_label("inlet_pressure") == "atm"

    with pytest.raises(RuntimeError):
        inp["inlet_pressure"] = "90010 [Pa]"
