"""
Classes for running a parametric study in Fluent.

Example
-------
>>> from ansys.fluent.parametric.local.local import LocalParametricStudy, run_local_study_in_fluent

>>> local_study = LocalParametricStudy(case_filepath="E:\elbow1_param.cas.h5")

>>> design_point = local_study.design_point("Base DP")
>>> design_point.input_parameters['v1'] = 0.0

>>> for idx in range(1, 20):
>>>    design_point = local_study.add_design_point("dp_"+str(idx))
>>>    design_point.input_parameters['v1'] = float(idx)/10.0
    
>>> run_local_study_in_fluent(local_study, 5)

>>> for design_point in local_study.design_point_table:
>>>    for k, v in design_point.input_parameters.items():
>>>        print("input parameter", k, v)
>>>    for k, v in design_point.output_parameters.items():
>>>        print("output parameter", k, v)
>>>    print(72 * "-")

"""

from enum import Enum
from math import ceil


from ansys.fluent.core.utils.async_execution import asynchronous

from .filereader.casereader import CaseReader

from ansys.fluent.parametric import ParametricSession
from ansys.fluent.parametric import BASE_DP_NAME


class LocalDesignPoint:
    """
    Purely local version of design point in a parametric study.

    Attributes
    ----------
    name : str
        Name of the design point as a str.
    output_parameters : dict
        Dict of output parameters
        (name of parameter to value).
    input_parameters : dict
        Dict of input parameters
        (name of parameter to value).
    status : DesignPointStatus
        Current status of the design point.
    """

    def __init__(self, design_point_name: str, base_design_point=None):
        self.name = design_point_name
        if base_design_point:
            self.__inputs = base_design_point.input_parameters.copy()
            self.__outputs = base_design_point.output_parameters.copy()
        else:
            self.__inputs = {}
            self.__outputs = {}

    @property
    def input_parameters(self) -> dict:
        return self.__inputs

    @input_parameters.setter
    def input_parameters(self, inputs: dict):
        self.__inputs = inputs

    @property
    def output_parameters(self) -> dict:
        return self.__outputs

    @output_parameters.setter
    def output_parameters(self, outputs: dict):
        self.__outputs = outputs


class LocalDesignPointTable(list):
    """
    Local version of Design point table in a parametric study

    Methods
    -------
    add_design_point(design_point_name: str) -> DesignPoint
        Add a new design point to the table with the provided name.
    find_design_point(idx_or_name)
        Get a design point, either by name (str) or an index
        indicating the position in the table (by order of insertion).
        Raises
        ------
        RuntimeError
            If the design point is not found.
    remove_design_point(idx_or_name)
        Remove a design point, either by name (str) or an index
        indicating the position in the table (by order of insertion).
        Raises
        ------
        RuntimeError
            If the design point is not found.
    """

    def __init__(self, base_design_point: LocalDesignPoint):
        super().__init__()
        self.append(base_design_point)

    def add_design_point(self, design_point_name: str) -> LocalDesignPoint:
        self.append(LocalDesignPoint(design_point_name, self[0]))
        return self[-1]

    def find_design_point(self, idx_or_name) -> LocalDesignPoint:
        if isinstance(idx_or_name, int):
            return self[idx_or_name]
        for design_point in self:
            if idx_or_name == design_point.name:
                return design_point
        raise RuntimeError(f"Design point not found: {idx_or_name}")

    def remove_design_point(self, idx_or_name):
        design_point = self.find_design_point(idx_or_name)
        if design_point is self[0]:
            raise RuntimeError("Cannot remove base design point")
        self.remove(self.find_design_point(idx_or_name))


class LocalParametricStudy:
    """
    Local version of parametric study that manages design points to parametrize a
    Fluent solver set-up.

    Methods
    -------
    add_design_point(design_point_name: str) -> LocalDesignPoint
        Add a design point
    design_point(idx_or_name)
        Get a design point, either by name (str) or an index
        indicating the position in the table (by order of insertion).
        Raises
        ------
        RuntimeError
            If the design point is not found.
    """

    def __init__(
        self,
        case_filepath: str,
        base_design_point_name: str = "Base DP"
    ):
        self.case_filepath = case_filepath
        base_design_point = LocalDesignPoint(base_design_point_name)
        case_reader = CaseReader(case_file_path=case_filepath)

        def input_parameter_info(parameter):
            name, value = None, None
            for k, v in parameter:
                if k == "name":
                    name = v
                elif k == "definition":
                    value = v
            return name, value

        def set_input_parameter_info(source, target):
            for parameter in source:
                target.update((input_parameter_info(parameter),))

        def output_parameter_info(parameter):
            parameter = parameter[1]
            for elem in parameter:
                if len(elem) and elem[0] == "name":
                    return elem[1][1], None

        def set_output_parameter_info(source, target):
            for parameter in source:
                target.update((output_parameter_info(parameter),))

        set_input_parameter_info(
            source=case_reader.input_parameters(),
            target=base_design_point.input_parameters)

        set_output_parameter_info(
            source=case_reader.output_parameters(),
            target=base_design_point.output_parameters)
        
        print(case_reader.output_parameters())

        self.design_point_table = LocalDesignPointTable(base_design_point)

    def add_design_point(self, design_point_name: str) -> LocalDesignPoint:
        return self.design_point_table.add_design_point(design_point_name)

    def design_point(self, idx_or_name) -> LocalDesignPoint:
        return self.design_point_table.find_design_point(idx_or_name)


def run_local_study_in_fluent(
    local_study,
    num_servers,
    capture_report_data=False):

    source_table_size = len(local_study.design_point_table)

    def make_input_for_study(design_point_range) -> None:
        if design_point_range is None:
            design_point_range = range(0, source_table_size)
        study_input = []
        for idx in design_point_range:
            design_point = local_study.design_point(idx_or_name = idx)
            study_input.append(design_point.input_parameters.copy())
        return study_input

    def make_input_for_studies(num_servers) -> None:
        study_inputs = []
        total_num_points = num_points = source_table_size
        for i in range(num_servers):
            count = ceil(num_points/num_servers)
            range_base = total_num_points - num_points
            num_points -= count
            num_servers -= 1
            study_inputs.append(make_input_for_study(
                range(range_base, range_base + count)
                ))
        return study_inputs

    @asynchronous
    def make_parametric_session(case_filepath):
        return ParametricSession(case_filepath=case_filepath)

    @asynchronous
    def apply_to_study(study, inputs):
        first = True
        for inpt in inputs:
            if first:
                design_point = study.design_points[BASE_DP_NAME]
                design_point.capture_simulation_report_data_enabled = (
                    capture_report_data
                )
                first = False
            else:
                design_point = study.add_design_point(
                    capture_simulation_report_data=capture_report_data
                    )
            design_point.input_parameters = inpt.copy()

    @asynchronous
    def update_design_point(study):
        study.update_all_design_points()

    def apply_to_studies(studies, inputs) -> None:
        results = []
        for item in list(zip(studies, inputs)):
            study, inpt = item
            results.append(apply_to_study(study, inpt))
        for result in results:
            result.result()

    study_inputs = make_input_for_studies(num_servers)

    sessions = []
    studies = []
    for i in range(num_servers):
        sessions.append(make_parametric_session(
            case_filepath=local_study.case_filepath
            ))

    for session in sessions:
        studies.append(next(iter(session.result().studies.values())))

    apply_to_studies(studies, study_inputs)

    updates = []
    for study in studies:
        updates.append(update_design_point(study))

    for update in updates:
        update.result()

    it = iter(local_study.design_point_table)

    for study in studies:
        for _, design_point in study.design_points.items():
            next(it).output_parameters = design_point.output_parameters.copy()






