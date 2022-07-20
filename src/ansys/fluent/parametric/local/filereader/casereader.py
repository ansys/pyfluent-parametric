import h5py

from . import lispy


class CaseReader:
    def __init__(self, case_file_path):
        file = h5py.File(case_file_path)
        settings = file["settings"]
        rpvars = settings["Rampant Variables"][0]
        rp_vars_str = rpvars.decode()
        self._rp_vars = lispy.parse(rp_vars_str)[1]

    def input_parameters(self):
        exprs = self._named_expressions()
        input_params = []
        for expr in exprs:
            for attr in expr:
                if attr[0] == "input-parameter" and attr[1] is True:
                    input_params.append(expr)
        return input_params

    def output_parameters(self):
        parameters = self._find_rp_var("parameters/output-parameters")
        return parameters

    def named_expressions(self):
        return self._named_expressions()

    def _named_expressions(self):
        return self._find_rp_var("named-expressions")

    def _find_rp_var(self, name: str):
        for var in self._rp_vars:
            if type(var) == list and len(var) and var[0] == name:
                return var[1]
