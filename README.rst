PyFluent-Parametric
===================
|pyansys| |pypi| |GH-CI| |MIT| |black| |pre-commit|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-fluent-parametric.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-fluent-parametric
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/pyfluent-parametric/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pyfluent-parametric/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |pre-commit| image:: https://results.pre-commit.ci/badge/github/ansys/pyfluent-parametric/main.svg
   :target: https://results.pre-commit.ci/latest/github/ansys/pyfluent-parametric/main
   :alt: pre-commit.ci status

Overview
--------
PyFluent-Parametric provides Pythonic access to Ansys Fluent's parametric
workflows.

Documentation and issues
------------------------
For comprehensive information on PyFluent-Parametric, see the latest
release `documentation <https://parametric.fluent.docs.pyansys.com>`_.

On the `PyFluent-Parametric Issues <https://github.com/ansys/pyfluent-parametric/issues>`_,
you can create issues to submit questions, report bugs, and request new features. To reach
the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

Installation
------------
The ``ansys-fluent-parametric`` package currently supports Python 3.8 through Python
3.11 on Windows and Linux.

Install the latest release from `PyPI
<https://pypi.org/project/ansys-fluent-parametric/>`_ with:

.. code:: console

   pip install ansys-fluent-parametric

Alternatively, install the latest from `GitHub
<https://github.com/ansys/pyfluent-parametric>`_ with:

.. code:: console

   pip install git+https://github.com/ansys/pyfluent-parametric.git

If you plan on doing local *development* of PyFluent with Git, install
with:

.. code:: console

   git clone https://github.com/ansys/pyfluent-parametric.git
   cd pyfluent-parametric
   pip install pip -U
   pip install -e .

Dependencies
------------
You must have a locally-installed, licensed copy of Ansys to run Fluent. The
first supported version is 2022 R2.

Getting started
---------------

Basic usage
~~~~~~~~~~~
The following code assumes that a PyFluent session has already been created and a Fluent case
with input parameters has been set up. For a full example, see `Defining Parametric Workflows
<https://fluentparametric.docs.pyansys.com/users_guide/parametric_workflows.html>`_ in
the PyFluent-Parametric documentation.

.. code:: python

   import ansys.fluent.core as pyfluent
   from ansys.fluent.parametric import ParametricStudy
   solver_session = pyfluent.launch_fluent(mode="solver")
   study = ParametricStudy(solver_session.parametric_studies).initialize()
   input_parameters_update = study.design_points["Base DP"].input_parameters
   input_parameters_update["inlet1_vel"] = 0.5
   study.design_points["Base DP"].input_parameters = input_parameters_update
   study.update_current_design_point()
   print(study.design_points["Base DP"].output_parameters)

License and acknowledgments
---------------------------
PyFluent-Parametric is licensed under the MIT license.

PyFluent-Parametric makes no commercial claim over Ansys whatsoever. This library
extends the functionality of Fluent by adding a Python interface to Fluent without
changing the core behavior or license of the original software. The use of the
interactive Fluent control of PyFluent-Parametric requires a legally licensed
local copy of Fluent.

For more information, see the `Ansys Fluent <https://www.ansys.com/products/fluids/ansys-fluent>`
page on the Ansys website.
