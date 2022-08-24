import ansys.fluent.core as pyfluent
from ansys.fluent.core.examples import download_file
import pytest

_static_mixer_parameters_filename = None


@pytest.fixture
def load_static_mixer_parameter(with_launching_container):
    session = pyfluent.launch_fluent(precision="double", processor_count=2)
    global _static_mixer_parameters_filename
    if not _static_mixer_parameters_filename:
        _static_mixer_parameters_filename = download_file(
            filename="Static_Mixer_Parameters.cas.h5",
            directory="pyfluent/static_mixer",
        )
    session.solver.root.file.read(
        file_type="case", file_name=_static_mixer_parameters_filename
    )
    yield session
    session.exit()
