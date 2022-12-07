"""Classes interfacing input and output parameters in Fluent.
"""

from collections.abc import Mapping, MutableMapping
from typing import Iterator, Union

from ansys.fluent.core.services.scheme_eval import Symbol
from ansys.fluent.core.session import Session

V = Union[int, float, str]


class _InputParametersSettingsImpl(MutableMapping):
    """
    InputParameters implementation using settings API
    """

    def __init__(self, named_expressions, unit_label_getter):
        self._named_expressions = named_expressions
        self._unit_label_getter = unit_label_getter

    def _get_input_parameter_names(self):
        return [
            k for k, v in self._named_expressions().items() if v.get("input_parameter")
        ]

    def __setitem__(self, name: str, value: V) -> None:
        if name not in self._get_input_parameter_names():
            raise LookupError(f"Input parameter {name} doesn't exist.")
        if not (
            isinstance(value, int) or isinstance(value, float) or isinstance(value, str)
        ):
            raise TypeError(f"Value {value} should be of type int, float or string.")
        # TODO: Check if the input str is of form "<float> [<valid unit label>]"
        if isinstance(value, int) or isinstance(value, float):
            unit_label = self._unit_label_getter(name)
            value = f"{value} [{unit_label}]" if unit_label else str(value)
        self._named_expressions[name].definition = value

    def __delitem__(self, name: str) -> None:
        raise NotImplementedError()

    def __getitem__(self, name: V) -> str:
        if name not in self._get_input_parameter_names():
            raise LookupError(f"Parameter {name} doesn't exist.")
        return self._named_expressions[name].definition()

    def __len__(self) -> int:
        return len(self._get_input_parameter_names())

    def __iter__(self) -> Iterator[str]:
        for name in self._get_input_parameter_names():
            yield name


class _InputParametersSchemeImpl(MutableMapping):
    """
    InputParameters implementation using scheme-eval API
    """

    def __init__(self, scheme_eval, unit_label_getter):
        self._scheme_eval = scheme_eval
        self._unit_label_getter = unit_label_getter

    def _get_parameter_names(self):
        parameter_names = (
            self._scheme_eval(
                "(send (get expressions-package named-expression-manager) get-names)"
            )
            or []
        )
        return parameter_names if parameter_names else []

    def __setitem__(self, name: str, value: V) -> None:
        if name not in self._get_parameter_names():
            raise LookupError(f"Input parameter {name} doesn't exist.")
        if not (
            isinstance(value, int) or isinstance(value, float) or isinstance(value, str)
        ):
            raise TypeError(f"Value {value} should be of type int, float or string.")
        # TODO: Check if the input str is of form "<float> [<valid unit label>]"
        if isinstance(value, int) or isinstance(value, float):
            unit_label = self._unit_label_getter(name)
            value = f"{value} [{unit_label}]" if unit_label else str(value)
        self._scheme_eval(
            f'(send (send (get expressions-package named-expression-manager) get-object-by-name "{name}") set-var! \'definition "{value}")'  # noqa: E501
        )

    def __delitem__(self, name: str) -> None:
        raise NotImplementedError()

    def __getitem__(self, name: str) -> V:
        if name not in self._get_parameter_names():
            raise LookupError(f"Input parameter {name} doesn't exist.")
        return self._scheme_eval(
            f'(send (send (get expressions-package named-expression-manager) get-object-by-name "{name}") get-var \'definition)'  # noqa: E501
        )

    def __len__(self) -> int:
        return len(self._get_parameter_names())

    def __iter__(self) -> Iterator[str]:
        for name in self._get_parameter_names():
            yield name


class InputParameters(MutableMapping):
    """Provides for accessing and modifying input parameter values in Fluent.

    Parameters
    ----------
    session : Session
        Connected Fluent session.

    Examples
    --------
    >>> inp = InputParameters(session)
    >>> print([(k, v) for k, v in inp.items()])
    [('parameter-1', '0.3 [m/s]'), ('parameter-2', '1.2 [m/s]')]
    >>> inp['parameter-1']
    '0.3 [m/s]'
    >>> inp['parameter-1'] = '0.5 [m/s]'
    >>> inp['parameter-1']
    '0.5 [m/s]'
    >>> inp.get_unit_label('parameter-1')
    'm/s'
    >>> inp['parameter-1'] = '40 [cm/s]'
    >>> inp['parameter-1']
    '40 [cm/s]'
    >>> inp.get_unit_label('parameter-1')
    'cm/s'
    >>> inp['parameter-1'] = 50
    >>> inp['parameter-1']
    '50 [cm/s]'

    """

    def __init__(self, session: Session):
        """Initialize input parameters.

        Parameters
        ----------
        session : Session
        Connected Fluent session.
        """
        self._session = session
        try:
            self._impl = _InputParametersSettingsImpl(
                self._session.setup.named_expressions, self.get_unit_label
            )
        except AttributeError:
            self._impl = _InputParametersSchemeImpl(
                self._session.scheme_eval.scheme_eval, self.get_unit_label
            )

    def get_unit_label(self, name: str) -> str:
        """Get the unit label of a Fluent input parameter.

        Parameters
        ----------
        name : str
            Name of the Fluent input parameter.

        Returns
        -------
        str
            Unit label of the Fluent input parameter.

        """
        value = str(self[name])
        value_split = value.split(maxsplit=1)
        if len(value_split) == 1:
            return ""
        else:
            return value_split[1].lstrip("[").rstrip("]")

    def __setitem__(self, name: str, value: V) -> None:
        """Set value of an input parameter.

        Parameters
        ----------
        name : str
            Name of the input parameter
        value: Union[int, float, str]
            Value in either integer, float or string format.
            Integer or float values are set in Fluent with unit-label returned by
            ``get_unit_label`` method.
            Strings are accepted in the form "<value> [<unit-label>]", e.g., "5 [m/s]".
            For Fluent 22.2, The unit-label should be same as unit-label returned by
            ``get_unit_label`` method
            For Fluent 23,1, the unit-label should be a valid unit-label in Fluent.

        """
        self._impl[name] = value

    def __delitem__(self, name: str) -> None:
        """Deletion is not supported."""
        raise RuntimeError(f"Cannot delete parameter {name}")

    def __getitem__(self, name: str) -> V:
        """Get value of an input parameter.

        Parameters
        ----------
        name : str
            Name of the input parameter

        Returns
        -------
        Union[int, float, str]
            Value of the input parameter
            If the parameter has units, a string in the form
            "<value> [<unit-label>]", e.g., "5 [m/s]" is returned.
            If the parameter doesn't have units, a real number is returned.

        """
        value = self._impl[name]
        try:
            return float(value)
        except ValueError:
            return value

    def __len__(self) -> int:
        """Get the number of input parameters.

        Returns
        -------
        int
            The number of input parameters.

        """
        return len(self._impl)

    def __iter__(self) -> Iterator[str]:
        """Get an iterator over input parameters.

        Returns
        -------
        Iterator[str]
            Iterator over input parameters

        """
        for name in self._impl:
            yield name


class OutputParameters(Mapping):
    """Provides for accessing output parameter values in Fluent.

    Parameters
    ----------
    session : Session
        Connected Fluent session.

    Examples
    --------
    >>> outp = OutputParameters(session)
    >>> print([(k, v) for k, v in outp.items()])
    [('report-def-1', '10 [Pa]'), ('report-def-2', '20 [Pa]')]
    >>> outp['report-def-1']
    '10 [Pa]'

    """

    def __init__(self, session: Session):
        """Initialize InputParameters.

        Parameters
        ----------
        session : Session
        Connected Fluent session.
        """
        self._session = session

    def _get_parameter_names(self):
        parameter_names = (
            self._session.scheme_eval.scheme_eval(
                "(map (lambda (p) (send p get-name)) (get-all-output-parameters))"
            )
            or []
        )
        return parameter_names if parameter_names else []

    def _get_unit_label(self, name: str) -> str:
        if name not in self._get_parameter_names():
            raise LookupError(f"Output parameter {name} doesn't exist.")
        unit_label = ""
        units = self._session.scheme_eval.scheme_eval(
            f'(send (get-output-parameter "{name}") get-units)'
        )
        if units:
            unit = units[0]
            if isinstance(unit, Symbol):
                unit = unit.str
            if isinstance(unit, str):
                unit_label = self._session.scheme_eval.scheme_eval(
                    f'(units/inquire-unit-label-string-for-quantity "{unit}")'
                )
        return unit_label

    def __getitem__(self, name: str) -> V:
        """Get the value of an output parameter.

        Parameters
        ----------
        name : str
            Name of the output parameter

        Returns
        -------
        Union[int, float, str]
            Value of the output parameter.
            If the parameter has units, a string in the form
            "<value> [<unit-label>]". For example ``"5 [m/s]"``.
            If the parameter does not have units, a real number is returned.

        """
        if name not in self._get_parameter_names():
            raise LookupError(f"Parameter {name} doesn't exist.")
        value = self._session.scheme_eval.scheme_eval(
            f'(get-output-parameter-value "{name}")'
        )
        unit_label = self._get_unit_label(name)
        return f"{value} [{unit_label}]" if unit_label else value

    def __len__(self) -> int:
        """Get the number of output parameters.

        Returns
        -------
        int
            Number of output parameters.

        """
        return len(self._get_parameter_names())

    def __iter__(self) -> Iterator[str]:
        """Get an iterator over output parameters.

        Returns
        -------
        Iterator[str]
            Iterator over output parameters.

        """
        for name in self._get_parameter_names():
            yield name
