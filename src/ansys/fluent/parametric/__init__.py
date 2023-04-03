"""Classes for running a parametric study in Fluent.

Example
-------
>>> from ansys.fluent.parametric import ParametricStudy

Instantiate the study from a Fluent session that has already read a case:

>>> study1 = ParametricStudy(session.parametric_studies).initialize()

Access and modify the input parameters of the base design point:

>>> ip = study1.design_points["Base DP"].input_parameters
>>> ip['vel_hot'] = 0.2
>>> study1.design_points["Base DP"].input_parameters = ip

Update the current design point:

>>> study1.update_current_design_point()

Access the output parameters of the base design point:

>>> study1.design_points["Base DP"].output_parameters

Create and update more design points, and then delete them:

>>> dp1 = study1.add_design_point()
>>> dp2 = study1.duplicate_design_point(dp1)
>>> study1.update_all_design_points()
>>> study1.delete_design_points([dp1, dp2])

Create, rename, and delete parametric studies:

>>> study2 = study1.duplicate()
>>> study2.rename("abc")
>>> study1.delete()

Project workflow

>>> from ansys.fluent.parametric import ParametricProject
>>> proj = ParametricProject(session.file.parametric_project, session.parametric_studies, "nozzle_para_named.flprj")  # noqa: E501
>>> proj.save()
>>> proj.save_as(project_filepath="nozzle_para_named1.flprj")
>>> proj.export(project_filepath="nozzle_para_named2.flprj")
>>> proj.archive()

Use a parametric session:

>>> from ansys.fluent.parametric import ParametricSession
>>> session1 = ParametricSession(case_filepath="elbow_params_2.cas.h5")
>>> session1.studies['elbow_params_2-Solve'].design_points['Base DP'].input_parameters  # noqa: E501
>>> study2 = session1.new_study()
>>> session2 = ParametricSession(project_filepath="nozzle_para_named.flprj")
"""
import logging
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional

import ansys.fluent.core as pyfluent

logger = logging.getLogger("ansys.fluent")

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

_VERSION_INFO = None
__version__ = importlib_metadata.version(__name__.replace(".", "-"))


def version_info() -> str:
    """Method returning the version of PyFluent being used.

    Returns
    -------
    str
        The PyFluent version being used.

    Notes
    -------
    Only available in packaged versions. Otherwise it will return __version__.
    """
    return _VERSION_INFO if _VERSION_INFO is not None else __version__


BASE_DP_NAME = "Base DP"


class DesignPoint:
    """Provides for accessing and modifying design points in a parametric study.

    Parameters
    ----------
    name : str
        Name of the design point.
    dp_settings

    """

    def __init__(self, name: str, study: Any):
        self.name = name
        self._study = study
        self._dp_settings = study.design_points[name]

    @property
    def input_parameters(self) -> Dict[str, float]:
        """Dictionary of input parameter values by name."""
        return self._dp_settings.input_parameters()

    @input_parameters.setter
    def input_parameters(self, value: Dict[str, float]) -> None:
        self._dp_settings.input_parameters = value

    @property
    def output_parameters(self) -> Dict[str, float]:
        """Dictionary of output parameter values by name."""
        return self._dp_settings.output_parameters()

    @property
    def write_data_enabled(self) -> bool:
        """Whether to write data for the design point."""
        return self._dp_settings.write_data()

    @write_data_enabled.setter
    def write_data_enabled(self, value: bool) -> None:
        self._dp_settings.write_data = value

    @property
    def capture_simulation_report_data_enabled(self) -> bool:
        """Whether to capture simulation report data for the design point."""
        return self._dp_settings.capture_simulation_report_data()

    @capture_simulation_report_data_enabled.setter
    def capture_simulation_report_data_enabled(self, value: bool) -> None:
        self._dp_settings.capture_simulation_report_data = value

    def set_as_current(self) -> None:
        """Set the design point as the current design point."""
        self._study.design_points.set_as_current(design_point=self.name)


class ParametricStudy:
    """Provides for managing parametric studies and their respective design points.

    A parametric study is used to parametrize design points in a Fluent solver
    set up. This class provides the ability to run Fluent for a series of
    design points and access or modify input and output parameters.

    Parameters
    ----------
    parametric_studies :

    session : Session, optional
        Connected Fluent session. The default is ``None``.
    name : str, optional
        Name of the parametric study. The default is ``None``.
    design_points : Dict[str, DesignPoint], optional
        Dictionary of design points under the parametric study by name.
        The default is ``None``.
    """

    def __init__(
        self,
        parametric_studies,
        session=None,
        name: Optional[str] = None,
        design_points: Dict[str, DesignPoint] = None,
    ):
        self._parametric_studies = parametric_studies
        self.session = (
            session if session is not None else (_shared_parametric_study_registry())
        )
        self.name = name
        self.design_points = {}
        if design_points is not None:
            self.design_points = design_points
        self.project_filepath = None
        self.session.register_study(self)

    def get_all_studies(self) -> Dict[str, "ParametricStudy"]:
        """Get all currently active studies.

        Returns
        -------
        Dict[str, "ParametricStudy"]
            Dictionary of all currently active studies.
        """
        return {v.name: v for _, v in self.session._all_studies.items()}

    def initialize(self) -> "ParametricStudy":
        """Initialize the parametric study."""
        if self._parametric_studies.initialize.is_active():
            self.project_filepath = Path(
                tempfile.mkdtemp(
                    prefix="project-",
                    suffix=".cffdb",
                    dir=str(Path.cwd()),  # TODO: should be cwd of server
                )
            )
            self.project_filepath.rmdir()
            old_study_names = self._parametric_studies.get_object_names()
            self._parametric_studies.initialize(
                project_filename=self.project_filepath.stem
            )
            new_study_names = self._parametric_studies.get_object_names()
            self.name = set(new_study_names).difference(set(old_study_names)).pop()
            base_design_point = DesignPoint(
                BASE_DP_NAME,
                self._parametric_studies[self.name],
            )
            self.design_points = {BASE_DP_NAME: base_design_point}
            self.session.current_study_name = self.name
            return self
        else:
            logging.error("Initialize is not available.")

    def rename(self, new_name: str) -> None:
        """Rename the parametric study.

        Parameters
        ----------
        new_name : str
            New name.
        """
        self._parametric_studies.rename(new_name, self.name)
        self.name = new_name
        self.design_points = {
            k: DesignPoint(k, self._parametric_studies[self.name])
            for k, _ in self.design_points.items()
        }

    @property
    def is_current(self) -> bool:
        """Whether the parametric study is the current parametric study."""
        return self.session.current_study_name == self.name

    def set_as_current(self) -> None:
        """Set the parametric study as the current parametric study."""
        if not self.is_current:
            self._parametric_studies.set_as_current(self.name)
            self.session.current_study_name = self.name

    def duplicate(self, copy_design_points: bool = True) -> "ParametricStudy":
        """Duplicate the current study.

        Parameters
        ----------
        copy_design_points : bool, optional
            Whether to copy the design points from the current study. The
            default is ``True``.

        Returns
        -------
        ParametricStudy
            New instance of the parametric study.
        """
        old_study_names = self._parametric_studies.get_object_names()
        self._parametric_studies.duplicate(copy_design_points=copy_design_points)
        new_study_names = self._parametric_studies.get_object_names()
        clone_name = set(new_study_names).difference(set(old_study_names)).pop()
        current_study = self.get_all_studies()[self.session.current_study_name]
        if copy_design_points:
            clone_design_points = {
                k: DesignPoint(k, self._parametric_studies[clone_name])
                for k, _ in current_study.design_points.items()
            }
        else:
            base_design_point = DesignPoint(
                BASE_DP_NAME,
                self._parametric_studies[clone_name],
            )
            clone_design_points = {BASE_DP_NAME: base_design_point}
        clone = ParametricStudy(
            self._parametric_studies, self.session, clone_name, clone_design_points
        )
        self.session.current_study_name = clone.name
        return clone

    def delete(self) -> None:
        """Delete the parametric study."""
        if self.is_current:
            logging.error("Cannot delete the current study %s", self.name)
        else:
            del self._parametric_studies[self.name]
            self.session._all_studies.pop(id(self))
            del self

    def use_base_data(self) -> None:
        """Use base data for the parametric study."""
        self._parametric_studies.use_base_data()

    def import_design_table(self, filepath: str) -> None:
        """Import the design table for the parametric study.

        Parameters
        ----------
        filepath : str
            Filepath for the design table.
        """
        self._parametric_studies.import_design_table(filepath=filepath)

    def export_design_table(self, filepath: str) -> None:
        """Export the design table for the parametric study.

        Parameters
        ----------
        filepath : str
            Filepath to export the design table to.
        """
        self._parametric_studies.export_design_table(filepath=filepath)

    @property
    def current_design_point(self) -> DesignPoint:
        """Get the current design point.

        This is the current design point within the design points under the
        parametric study.
        """
        dp_name = self._parametric_studies[self.name].current_design_point()
        return self.design_points[dp_name]

    def add_design_point(
        self,
        write_data: bool = False,
        capture_simulation_report_data: bool = True,
    ) -> DesignPoint:
        """Add a new design point under the parametric study.

        Parameters
        ----------
        write_data : bool, optional
            Whether to write data for the design point. The default
            is ``False``.
        capture_simulation_report_data : bool, optional
            Whether to capture simulation report data for the design
            point. The default is ``True``.

        Returns
        -------
        DesignPoint
            New design point.
        """
        self.set_as_current()
        dp_settings = self._parametric_studies[self.name].design_points
        dps_before = dp_settings.get_object_names()
        dp_settings.create_1(
            write_data=write_data,
            capture_simulation_report_data=capture_simulation_report_data,
        )
        dps_after = dp_settings.get_object_names()
        dp_name = set(dps_after).difference(set(dps_before)).pop()
        design_point = DesignPoint(
            dp_name,
            self._parametric_studies[self.name],
        )
        self.design_points[dp_name] = design_point
        return design_point

    def delete_design_points(self, design_points: List[DesignPoint]) -> None:
        """Delete a list of design points.

        Parameters
        ----------
        design_points : List[DesignPoint]
            List of design points to delete.
        """
        if self.current_design_point in design_points:
            logging.error(
                "Cannot delete the current design point %s",
                self.current_design_point.name,
            )
            design_points.remove(self.current_design_point)
        dp_settings = self._parametric_studies[self.name].design_points
        dp_settings.delete_design_points(
            design_points=[dp.name for dp in design_points]
        )
        for design_point in design_points:
            self.design_points.pop(design_point.name)
            del design_point

    def duplicate_design_point(self, design_point: DesignPoint) -> DesignPoint:
        """Duplicate the design point.

        Parameters
        ----------
        design_point : DesignPoint
            Design point.

        Returns
        -------
        DesignPoint
            New design point.
        """
        dp_settings = self._parametric_studies[self.name].design_points
        dps_before = dp_settings.get_object_names()
        dp_settings.duplicate(design_point=design_point.name)
        dps_after = dp_settings.get_object_names()
        new_dp_name = set(dps_after).difference(set(dps_before)).pop()
        new_dp = DesignPoint(
            new_dp_name,
            self._parametric_studies[self.name],
        )
        self.design_points[new_dp_name] = new_dp
        return new_dp

    def save_journals(self, separate_journals: bool) -> None:
        """Save journals.

        Parameters
        ----------
        separate_journals : bool
            Whether to save a separate journal for each design point.
        """
        dp_settings = self._parametric_studies[self.name].design_points
        dp_settings.save_journals(separate_journals=separate_journals)

    def clear_generated_data(self, design_points: List[DesignPoint]) -> None:
        """Clear the generated data for a list of design points.

        Parameters
        ----------
        design_points : List[DesignPoint]
            List of design points.
        """
        dp_settings = self._parametric_studies[self.name].design_points
        dp_settings.clear_generated_data(
            design_points=[dp.name for dp in design_points]
        )

    def load_current_design_point_case_data(self) -> None:
        """Load case data of the current design point."""
        dp_settings = self._parametric_studies[self.name].design_points
        dp_settings.load_case_data()

    def update_current_design_point(self) -> None:
        """Update the current design point."""
        dp_settings = self._parametric_studies[self.name].design_points
        dp_settings.update_current()

    def update_all_design_points(self) -> None:
        """Update all design points."""
        dp_settings = self._parametric_studies[self.name].design_points
        dp_settings.update_all()

    def update_selected_design_points(self, design_points: List[DesignPoint]) -> None:
        """Update a list of design points.

        Parameters
        ----------
        design_points : List[str]
            List of design points.
        """
        dp_settings = self._parametric_studies[self.name].design_points
        dp_settings.update_selected(design_points=[dp.name for dp in design_points])


class ParametricProject:
    """Provides the parametric project workflow.

    Attributes
    ----------
    project_filepath : str
        Filepath of the project.

    Methods
    -------
    open(project_filepath, load_case)
        Open a project.
    save()
        Save a project.
    save_as(project_filepath)
        Save a project as another project.
    export(project_filepath, convert_to_managed)
        Save a project as a copy.
    archive(archive_name)
        Archive a project.
    """

    def __init__(
        self,
        parametric_project,
        parametric_studies,
        project_filepath: str,
        session=None,
        open_project: bool = True,
    ):
        self._parametric_project = parametric_project
        self._parametric_studies = parametric_studies
        self.project_filepath = project_filepath
        self.session = (
            session if session is not None else (_shared_parametric_study_registry())
        )
        if open_project:
            self.open(project_filepath=project_filepath)

    def open(
        self, project_filepath: str = "default.flprj", load_case: bool = True
    ) -> None:
        """Open a project.

        Parameters
        ----------
        project_filepath : str, optional
            Project filename. The default is ``"default.flprj"``.
        load_case : bool, optional
            Whether to load the current case. The default ``True``.
        """
        self._parametric_project.open(
            project_filename=str(Path(project_filepath).resolve()),
            load_case=load_case,
        )
        self.project_filepath = project_filepath
        for study_name in self._parametric_studies.get_object_names():
            study = ParametricStudy(self._parametric_studies, self.session, study_name)
            dps_settings = self._parametric_studies[study_name].design_points
            for dp_name in dps_settings.get_object_names():
                study.design_points[dp_name] = DesignPoint(
                    dp_name, self._parametric_studies[study_name]
                )

    def save(self) -> None:
        """Save the project."""
        self._parametric_project.save()

    def save_as(self, project_filepath: str) -> None:
        """Save the project as another project.

        Parameters
        ----------
        project_filepath : str
            Filepath to save the new project to.
        """
        self._parametric_project.save_as(project_filename=project_filepath)

    def export(self, project_filepath: str, convert_to_managed: bool = False) -> None:
        """Save the project as a copy.

        Parameters
        ----------
        project_filepath : str
            Name for the new project.
        convert_to_managed : bool
            Whether to convert the project to a managed project.
        """
        self._parametric_project.save_as_copy(
            project_filename=project_filepath,
            convert_to_managed=convert_to_managed,
        )

    def archive(self, archive_path: str = None) -> None:
        """Archive the project.

        Parameters
        ----------
        archive_name : str, optional
            Mame of the archive file.
        """
        if not archive_path:
            archive_path = str(Path(self.project_filepath).with_suffix(".flprz"))
        self._parametric_project.archive(archive_name=archive_path)


class ParametricSessionLauncher:
    """Provides for launcheing Fluent for parametric sessions.

    Methods
    -------
    __call__(*args, **kwargs)
        Launch a Fluent session.
    """

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __call__(self):
        self._kwargs["mode"] = "solver"
        return pyfluent.launch_fluent(*self._args, **self._kwargs)


class ParametricStudyRegistry:
    def __init__(self):
        self._all_studies: Dict[int, "ParametricStudy"] = {}
        self.current_study_name = None

    def register_study(self, study):
        self._all_studies[id(study)] = study


class ParametricSession(ParametricStudyRegistry):
    """Provides for encapsulating studies and projects.

    Attributes
    ----------
    studies : Dict[str, ParametricStudy]
        Dictionary of parametric studies by their names within the session.
    project : ParametricProject
        Name of the parametric project if a project file is to be read.

    Methods
    -------
    new_study()
        Create a study.
    delete_study(self, study_name)
        Delete a study.
    rename_study(self, new_name, old_name)
        Rename a study.
    start_transcript()
        Start streaming of a Fluent transcript.
    stop_transcript()
        Stop streaming of a Fluent transcript.
    """

    def __init__(
        self,
        case_filepath: str = None,
        project_filepath: str = None,
        launcher: Any = ParametricSessionLauncher(),
        start_transcript: bool = False,
    ):
        """Instantiate a ParametricSession.

        Parameters
        ----------
        case_filepath : str, optional
            Case file name. The default is ``None``.
        project_filepath : str, optional
            Project file name. The default is ``None``.
        launcher : _type_, optional
            Fluent launcher. The default is ``ParametricSessionLauncher()``.
        start_transcript : bool, optional
            Whether to start streaming of a Fluent transcript. The default
            is ``False``.
        """
        super().__init__()
        self.studies = {}
        self.project = None
        self._session = launcher()
        self.scheme_eval = self._session.scheme_eval.scheme_eval
        self.scheme_eval(
            "(set parametric-study-dependents-manager " "save-project-at-exit? #f)"
        )
        if not start_transcript:
            self.stop_transcript()
        if case_filepath is not None:
            self._session.file.read(file_name=case_filepath, file_type="case")
            study = ParametricStudy(self._session.parametric_studies, self).initialize()
            self.studies[study.name] = study
            self.project = ParametricProject(
                parametric_project=self._session.file.parametric_project,
                parametric_studies=self._session.parametric_studies,
                project_filepath=str(study.project_filepath),
                open_project=False,
                session=self,
            )
        elif project_filepath is not None:
            self.project = ParametricProject(
                parametric_project=self._session.file.parametric_project,
                parametric_studies=self._session.parametric_studies,
                project_filepath=project_filepath,
                session=self,
            )
            studies_settings = self._session.parametric_studies
            for study_name in studies_settings.get_object_names():
                study = ParametricStudy(studies_settings, self, study_name)
                dps_settings = studies_settings[study_name].design_points
                for dp_name in dps_settings.get_object_names():
                    study.design_points[dp_name] = DesignPoint(
                        dp_name, studies_settings[study_name]
                    )
                self.studies[study_name] = study
            self.current_study_name = self._session.current_parametric_study()

    def new_study(self) -> ParametricStudy:
        """Create a new study.

        Returns
        -------
        ParametricStudy
            New study.
        """
        study = self.studies[self.current_study_name].duplicate()
        self.studies[study.name] = study
        return study

    def delete_study(self, study_name: str) -> None:
        """Delete a study.

        Parameters
        ----------
        study_name : str
            Study name.
        """
        study = self.studies[study_name]
        if study.is_current:
            logging.error("Cannot delete the current study %s", study_name)
        else:
            study.delete()
            self.studies.pop(study_name)

    def rename_study(self, new_name: str, old_name: str) -> None:
        """Rename a study.

        Parameters
        ----------
        new_name : str
            New name.
        old_name : str
            Current name.
        """
        study = self.studies.pop(old_name)
        study.rename(new_name)
        self.studies[new_name] = study

    def exit(self) -> None:
        self._session.exit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        self._session.exit()

    def start_transcript(self) -> None:
        """Start streaming of a Fluent transcript."""
        self._session.start_transcript()

    def stop_transcript(self) -> None:
        """Stop streaming of a Fluent transcript."""
        self._session.stop_transcript()


def _shared_parametric_study_registry():
    if _shared_parametric_study_registry.instance is None:
        _shared_parametric_study_registry.instance = ParametricStudyRegistry()
    return _shared_parametric_study_registry.instance


_shared_parametric_study_registry.instance = None


from ansys.fluent.parametric.parameters import InputParameters, OutputParameters
