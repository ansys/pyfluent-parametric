.. _ref_contributing:

============
Contributing
============
Overall guidance on contributing to a PyAnsys library appears in
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar with
this guide, paying particular attention to `Coding Style
<https://dev.docs.pyansys.com/coding-style/index.html#coding-style>`_
before attempting to contribute to PyFluent-Parametric.
 
The following contribution information is specific to PyFluent-Parametric.

Clone the repository
-----------------------
To clone and install the latest version of PyFluent-Parametric in
development mode, run:

.. code::

   git clone https://github.com/pyansys/pyfluent-parametric.git
   cd pyfluent-parametric
   pip install pip -U
   pip install -e .

Build documentation
-------------------
To build the PyFluent-Parametric documentation locally, in the root
directory of the repository, run:

.. code:: 

    pip install -r requirements/requirements_doc.txt
    cd doc
    make html

After the build completes, the HTML documentation is located in the
``_builds/html`` directory. You can load the ``index.html`` file 
in this directory into a web browser.

You can clear all HTML files from the ``_builds/html`` directory with:

.. code::

    make clean

Post issues
-----------
Use the `PyFluent-Parametric Issues <https://github.com/pyansys/pyfluent-parametric/issues>`_
page to submit questions, report bugs, and request new features.


Adhere to code style
--------------------
PyFluent-Parametric is compliant with `PyAnsys code style
<https://dev.docs.pyansys.com/coding_style/index.html>`_. It uses the tool
`pre-commit <https://pre-commit.com/>`_ to check the code style. You can install
and activate this tool with:

.. code:: bash

   python -m pip install pre-commit
   pre-commit install

You can then use the ``style`` rule defined in the ``Makefile`` with:

.. code:: bash

   make style

Or, you can directly run `pre-commit <https://pre-commit.com/>`_ with:

.. code:: bash

   pre-commit run --all-files --show-diff-on-failure
