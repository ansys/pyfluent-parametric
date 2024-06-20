.. _getting_started:

===============
Getting started
===============
PyFluent-Parametric provides for scripting parametric studies using Ansys Fluent.

To run PyFluent-Parametric, you must have a local copy of Ansys Fluent
2022 R2 or later licensed on your machine.

For more information, see the `Ansys Fluent <https://www.ansys.com/products/fluids/ansys-fluent>`_
page on the Ansys website.

***************
Install package
***************
The ``ansys-fluent-parametric`` package supports Python 3.10 through Python 3.13
on Windows and Linux.

Install the latest release from `PyPi
<https://pypi.org/project/ansys-fluent-parametric/>`_ with:

.. code::

   pip install ansys-fluent-parametric

Alternatively, install the latest release from `GitHub
<https://github.com/ansys/pyfluent-parametric/issues>`_ with:

.. code::

   pip install git+https://github.com/ansys/pyfluent-parametric.git


For a local *development* version, install with:

.. code::

   git clone https://github.com/ansys/pyfluent-parametric.git
   cd pyfluent-parametric
   pip install -e .


Any changes that you make locally are reflected in your setup after you restart
the Python kernel.

If you want to interact with the Fluent graphical user interface, set the
following environment variable:

.. code::

  set PYFLUENT_SHOW_SERVER_GUI=1    # Windows
  export PYFLUENT_SHOW_SERVER_GUI=1 # Linux (bash)

If you want to print the debug information for development, set the following
environment variable:

.. code:: python

  pyfluent.set_log_level('DEBUG') # for development, by default only errors are shown
