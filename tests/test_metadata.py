from ansys.fluent.parametric import __version__


def test_pkg_version():
    assert __version__ == "0.11.dev0"
