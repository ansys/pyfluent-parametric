"""Classes interfacing input and output parameters in Fluent.
"""

from collections.abc import Mapping, MutableMapping
from typing import Iterator, Union

from ansys.fluent.core.services.scheme_eval import Symbol
from ansys.fluent.core.session import Session

V = Union[str, float]


class _InputParametersSettingsImpl(MutableMapping):
    """
    InputParameters implementation using settings API
    """

    def __init__(self, named_expressions, unit_label_getter):
        self._named_expressions = named_expressions
        self._unit_label_getter = unit_label_getter

    def __setitem__(self, name: str, value: V) -> None:
        if name not in list(self._impl.keys()):
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
        raise NotImplementedError()

    def __len__(self) -> int:
        return len(self._named_expressions)

    def __iter__(self) -> Iterator[str]:
        for name in self._named_expressions:
            yield name


class _InputParametersSchemeImpl(MutableMapping):
    """
    InputParameters implementation using scheme-eval API
    """

    def __init__(self, scheme_eval, unit_label_getter):
        self._scheme_eval = scheme_eval
        self._unit_label_getter = unit_label_getter

    def _get_parameter_names(self):
        return self._scheme_eval(
            "(map (lambda (p) (send p get-name)) (get-all-input-parameters))"
        )

    def __setitem__(self, name: str, value: V) -> None:
        if name not in self._get_parameter_names():
            raise LookupError(f"Input parameter {name} doesn't exist.")
        if not (
            isinstance(value, int) or isinstance(value, float) or isinstance(value, str)
        ):
            raise TypeError(f"Value {value} should be of type int, float or string.")
        if isinstance(value, str):
            value, label = value.split(maxsplit=1)
            label = label.lstrip("[").rstrip("]")
            unit_label = self._unit_label_getter(name)
            if unit_label != label:
                raise RuntimeError(
                    "Input unit {label} doesn't match with system unit {unit_label}."
                )
            value = float(value)
        self._scheme_eval(f'(set-input-parameter-value "{name}" {value})')

    def __delitem__(self, name: str) -> None:
        raise NotImplementedError()

    def __getitem__(self, name: str) -> str:
        raise NotImplementedError()

    def __len__(self) -> int:
        return len(self._get_parameter_names())

    def __iter__(self) -> Iterator[str]:
        for name in self._get_parameter_names():
            yield name


class InputParameters(MutableMapping):
    """Class to access and modify input parameter values in Fluent.

    Methods
    -------
    get_unit_label(name)
        Get Fluent's unit label of an input parameter.
    __setitem__(name, value)
        Set value of an input parameter.
    __getitem__(name)
        Get value of an input parameter.
    __len__()
        Get the number of input parameters.
    __iter__()
        Get an iterator over input parameters.

    Examples
    --------
    >>> inp = InputParameters(session)
    >>> print([(k, v) for k, v in inp.items()])
    [('parameter-1', '0.3 [m/s]'), ('parameter-2', '1.2 [m/s]')]
    >>> inp['parameter-1']
    '0.3 [m/s]'
    >>> inp['parameter-1'] = '40 [cm/s]'
    >>> inp['parameter-1']
    '0.4 [m/s]'
    >>> inp.get_unit_label('parameter-1')
    'm/s'
    >>> inp['parameter-1'] = 0.5
    >>> inp['parameter-1']
    '0.5 [m/s]'

    """

    def __init__(self, session: Session):
        """Initialize InputParameters.

        Parameters
        ----------
        session : Session
        The connected Fluent session
        """
        self._session = session
        try:
            self._impl = _InputParametersSettingsImpl(
                self._session.solver.root.setup.named_expressions, self.get_unit_label
            )
        except AttributeError:
            self._impl = _InputParametersSchemeImpl(
                self._session.scheme_eval.scheme_eval, self.get_unit_label
            )

    def get_unit_label(self, name: str) -> str:
        """Get Fluent's unit label of an input parameter.

        Parameters
        ----------
        name : str
            Name of the input parameter

        Returns
        -------
        str
            Fluent's unit label

        """
        if name not in list(self._impl.keys()):
            raise LookupError(f"Input parameter {name} doesn't exist.")
        unit_label = ""
        units = self._session.scheme_eval.scheme_eval(
            f'(send (get-input-parameter "{name}") get-units)'
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

    def __setitem__(self, name: str, value: V) -> None:
        """Set value of an input parameter.

        Parameters
        ----------
        name : str
            Name of the input parameter
        value: Union[str, float]
            Value in either string or float format.
            Strings are accepted in the form "<value> [<unit-label>]", e.g., "5 [m/s]".
            The unit-label should be a valid unit-label in Fluent.
            Float values are set in Fluent with unit-label returned by
            ``get_unit_label`` method.

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
        Union[str, float]
            Value of the input parameter
            If the parameter has units, a string in the form
            "<value> [<unit-label>]", e.g., "5 [m/s]" is returned.
            If the parameter doesn't have units, a real number is returned.

        """
        if name not in list(self._impl.keys()):
            raise LookupError(f"Parameter {name} doesn't exist.")
        value = self._session.scheme_eval.scheme_eval(
            f'(get-input-parameter-value "{name}")'
        )
        unit_label = self.get_unit_label(name)
        return f"{value} [{unit_label}]" if unit_label else value

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
    """Class to access output parameter values in Fluent.

    Methods
    -------
    __getitem__(name)
        Get value of an output parameter.
    __len__()
        Get the number of output parameters.
    __iter__()
        Get an iterator over output parameters.

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
        The connected Fluent session
        """
        self._session = session

    def _get_parameter_names(self):
        return self._session.scheme_eval.scheme_eval(
            "(map (lambda (p) (send p get-name)) (get-all-output-parameters))"
        )

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
        """Get value of an output parameter.

        Parameters
        ----------
        name : str
            Name of the output parameter

        Returns
        -------
        Union[str, float]
            Value of the output parameter
            If the parameter has units, a string in the form
            "<value> [<unit-label>]", e.g., "5 [m/s]" is returned.
            If the parameter doesn't have units, a real number is returned.

        """
        if name not in self._get_parameter_names():
            raise LookupError(f"Parameter {name} doesn't exist.")
        value = self._session.scheme_eval.scheme_eval(
            f'(send (get-output-parameter "{name}") get-parameter-value)'
        )
        unit_label = self._get_unit_label(name)
        return f"{value} [{unit_label}]" if unit_label else value

    def __len__(self) -> int:
        """Get the number of output parameters.

        Returns
        -------
        int
            The number of output parameters.

        """
        return len(self._get_parameter_names())

    def __iter__(self) -> Iterator[str]:
        """Get an iterator over output parameters.

        Returns
        -------
        Iterator[str]
            Iterator over output parameters

        """
        for name in self._get_parameter_names():
            yield name
