.. _getting_started:

===============
Getting Started
===============
To run pyfluent-parametric, you must have a local licensed copy of Ansys Fluent. 
pyfluent-parametric supports Ansys Fluent versions 2022 R2 or newer.

Visit `Ansys <https://www.ansys.com/>`_ for more information on
getting a licensed copy of Ansys Fluent.

************
Installation
************

Python Module
~~~~~~~~~~~~~
The ``ansys-fluent-parametric`` package currently supports Python 3.7 through
Python 3.10 on Windows and Linux.

Install the latest release from `PyPi
<https://pypi.org/project/ansys-fluent-core/>`_ with:

.. code::

   pip install ansys-fluent-core

Alternatively, install the latest from `pyfluent-parametric GitHub
<https://github.com/pyansys/pyfluent-parametric/issues>`_ via:

.. code::

   pip install git+https://github.com/pyansys/pyfluent-parametric.git


For a local "development" version, install with:

.. code::

   git clone https://github.com/pyansys/pyfluent-parametric.git
   cd pyfluent
   pip install -e .

(Remove this section when PyFluent project goes public) 
Until PyFluent project goes public, install the latest release from
the artifactory.

.. code::

   python -m pip install --extra-index-url http://conanreader:conanreader@canartifactory.ansys.com:8080/artifactory/api/pypi/pypi/simple --trusted-host canartifactory.ansys.com ansys-fluent-parametric

This will allow you to install the PyFluent ``ansys-fluent-parametric`` module
and modify it locally and have the changes reflected in your setup
after restarting the Python kernel.

Add parametric documentation here.

If you want to interact with the Fluent graphical user interface, set the
following environment variable:

.. code::

  set PYFLUENT_SHOW_SERVER_GUI=1    # Windows
  export PYFLUENT_SHOW_SERVER_GUI=1 # Linux (bash)

If you want to print the debug information for development, set the following
environment variable:

.. code:: python

  pyfluent.set_log_level('DEBUG') # for development, by default only errors are shown