PyFluent Parametric
===================
|pyansys| |pypi| |GH-CI| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |pypi| image:: https://img.shields.io/pypi/v/pyfluent-parametric.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/pyfluent-parametric
   :alt: PyPI

.. |GH-CI| image:: https://github.com/pyansys/pyfluent-parametric/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/pyansys/pyfluent-parametric/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

Overview
--------
The PyFluent Parametric project provides Pythonic access to Ansys Fluent's parametric
workflows.

Documentation and Issues
------------------------
Please see the latest release `documentation <https://fluentparametric.docs.pyansys.com>`_
page for more details.

Please feel free to post issues and other questions at `PyFluent Parametric Issues
<https://github.com/pyansys/pyfluent-parametric/issues>`_.  This is the best place
to post questions and code.

Installation
------------
The ``ansys-fluent-parametric`` package currently supports Python 3.7 through Python
3.10 on Windows and Linux.

If you want to use PyFluent parametric please install the latest from `PyFluent Parametric GitHub
<https://github.com/pyansys/pyfluent-parametric>`_ via:

.. code:: console

   pip install git+https://github.com/pyansys/pyfluent-parametric.git

If you plan on doing local "development" of PyFluent with Git, then install
with:

.. code:: console

   git clone https://github.com/pyansys/pyfluent-parametric.git
   cd pyfluent-parametric
   pip install pip -U
   pip install install_data/ansys_api_fluent-0.1.0-py3-none-any.whl  # till public release
   pip install -e .

Dependencies
------------
You will need a locally installed licensed copy of ANSYS to run Fluent, with the
first supported version being Ansys 2022 R2.

Getting Started
---------------

Basic Usage
~~~~~~~~~~~

.. code:: python

   from ansys.fluent.parametric import ParametricStudy
   study_1 = ParametricStudy(session.solver.root.parametric_studies).initialize()
   input_parameters_update = study_1.design_points["Base DP"].input_parameters
   input_parameters_update["inlet1_vel"] = 0.5
   study_1.design_points["Base DP"].input_parameters = input_parameters_update
   study_1.update_current_design_point()
   print(study_1.design_points["Base DP"].output_parameters)

Above code assumes that a PyFluent session has already been created and a Fluent case
with input parameters has been set up. The `Defining Parametric Workflows
<https://fluentparametric.docs.pyansys.com/users_guide/parametric_workflows.html>`_ in
the user guide has a complete example.

License and Acknowledgments
---------------------------
``PyFluent Parametric`` is licensed under the MIT license.

This module, ``ansys-fluent-parametric`` makes no commercial claim over Ansys
whatsoever. This tool extends the functionality of ``Fluent`` by adding a Python
interface to the Fluent without changing the core behavior or license of the original
software.  The use of the interactive Fluent control of ``PyFluent Parametric`` requires
a legally licensed local copy of Ansys.

To get a copy of Ansys, please visit `Ansys <https://www.ansys.com/>`_.
