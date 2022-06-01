from email.headerregistry import Group
from pathlib import Path

from ansys.fluent.core.solver.flobject import Boolean, Command, Group, NamedObject, String
import pytest
from pytest_mock import MockerFixture

from ansys.fluent.parametric import ParametricProject


class root(Group):
    class file(Group):
        class parametric_project(Group):
            class open(Command):
                class project_filename(String):
                    pass

                class load_case(Boolean):
                    pass

                argument_names = ["project_filename", "load_case"]
                project_filename = project_filename
                load_case = load_case

            class save(Command):
                pass

            class save_as(Command):
                class project_filename(String):
                    pass

                argument_names = ["project_filename"]
                project_filename = project_filename

            class save_as_copy(Command):
                class project_filename(String):
                    pass

                argument_names = ["project_filename"]
                project_filename = project_filename

            class export(Command):
                class project_filename(String):
                    pass

                argument_names = ["project_filename"]
                project_filename = project_filename

            class archive(Command):
                class archive_name(String):
                    pass

                argument_names = ["archive_name"]
                archive_name = archive_name

            command_names = ["open", "save", "save_as", "save_as_copy", "export", "archive"]
            open = open

    class parametric_studies(NamedObject):
        pass

    child_names = ["file", "parametric_studies"]
    file = file
    parametric_studies = parametric_studies


@pytest.fixture(autouse=True)
def mock_settings_service(mocker: MockerFixture) -> None:
    Command.__call__ = mocker.Mock(return_value=None)
    NamedObject.get_object_names = mocker.Mock(return_value=[])


@pytest.fixture(name="parametric_project")
def fixture_parametric_project() -> ParametricProject:
    return ParametricProject(
        root.file.parametric_project(), root.parametric_studies(), "abc.flprj", False
    )


class TestParamtericProject:
    def test_open(
        self,
        mocker: MockerFixture,
        parametric_project: ParametricProject,
    ) -> None:
        spy = mocker.spy(root.file.parametric_project.open, "__call__")
        project_filepath = "abc.flprj"
        parametric_project.open(project_filepath=project_filepath)
        spy.assert_called_once_with(
            project_filename=str(Path(project_filepath).resolve()),
            load_case=True,
        )

    def test_save(
        self,
        mocker: MockerFixture,
        parametric_project: ParametricProject,
    ) -> None:
        spy = mocker.spy(root.file.parametric_project.save, "__call__")
        parametric_project.save()
        spy.assert_called_once_with()

    def test_save_as(
        self,
        mocker: MockerFixture,
        parametric_project: ParametricProject,
    ) -> None:
        spy = mocker.spy(root.file.parametric_project.save_as, "__call__")
        parametric_project.save_as(project_filepath="abc.flprj")
        spy.assert_called_once_with(project_filename="abc.flprj")

    def test_export(
        self,
        mocker: MockerFixture,
        parametric_project: ParametricProject,
    ) -> None:
        spy = mocker.spy(root.file.parametric_project.save_as_copy, "__call__")
        parametric_project.export(project_filepath="abc.flprj")
        spy.assert_called_once_with(project_filename="abc.flprj", convert_to_managed=False)

    def test_archive(
        self,
        mocker: MockerFixture,
        parametric_project: ParametricProject,
    ) -> None:
        spy = mocker.spy(root.file.parametric_project.archive, "__call__")
        parametric_project.archive()
        spy.assert_called_once_with(archive_name="abc.flprz")
