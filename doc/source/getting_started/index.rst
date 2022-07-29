.. _getting_started:

===============
Getting started
===============
To run PyFluent-Parametric, you must have a local licensed copy of Ansys Fluent. 
PyFluent-Parametric supports Ansys Fluent versions 2022 R2 or newer.

Visit `Ansys <https://www.ansys.com/>`_ for more information on
getting a licensed copy of Ansys Fluent.

************
Installation
************

Python module
~~~~~~~~~~~~~
The ``ansys-fluent-parametric`` package currently supports Python 3.7 through
Python 3.10 on Windows and Linux.

Install the latest release from `PyPi
<https://pypi.org/project/ansys-fluent-parametric/>`_ with:

.. code::

   pip install ansys-fluent-parametric

Alternatively, install the latest version from `GitHub
<https://github.com/pyansys/pyfluent-parametric/issues>`_ via:

.. code::

   pip install git+https://github.com/pyansys/pyfluent-parametric.git


For a local "development" version, install with:

.. code::

   git clone https://github.com/pyansys/pyfluent-parametric.git
   cd pyfluent-parametric
   pip install -e .

Follow `README.rst. <https://github.com/pyansys/pyfluent-parametric/blob/main/README.rst>`_.

This allows you to install the PyFluent Parametric ``ansys-fluent-parametric`` module
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
