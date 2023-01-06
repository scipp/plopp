.. raw:: html

   <div style="display: block; margin-left: auto; margin-right: auto; width: 60%;">
      <img src="_static/logo.svg" width="100%" />
   </div>
   <style> .transparent {opacity:0; font-size:16px} </style>

.. role:: transparent

:transparent:`Plopp`
********************

**Plopp** is the new data visualization framework for the `Scipp <https://scipp.github.io>`_ project.

Installation
============

Using pip
---------

You can install from ``pip`` using

.. code-block:: sh

   pip install plopp[scipp]

This will install both ``plopp`` and ``scipp`` which is required to use ``plopp``.
If you already have ``scipp`` installed, you can leave the ``[scipp]`` part out:

.. code-block:: sh

   pip install plopp

By default, this will only install minimal requirements which will allow you to create
static 1d and 2d plots.
If you wish to use additional features (interactive figures and 3d rendering),
you can install all the optional dependencies by doing

.. code-block:: sh

   pip install plopp[all]

Using conda
-----------

You can install from ``conda`` using

.. code-block:: sh

   conda install -c conda-forge -c scipp plopp

Get in touch
============

- If you have questions that are not answered by these documentation pages, ask on `GitHub discussions <https://github.com/scipp/plopp/discussions>`_.
  Please include a self-contained reproducible example if possible.
- Report bugs (including unclear, missing, or wrong documentation!), suggest features or view the source code `on GitHub <https://github.com/scipp/plopp>`_.

.. toctree::
   :caption: User Guide
   :maxdepth: 3
   :hidden:

   user-guide/line-plot
   user-guide/image-plot
   user-guide/slicer-plot
   user-guide/inspector-plot
   user-guide/super-plot
   user-guide/scatter3d-plot

.. toctree::
   :caption: Examples
   :maxdepth: 3
   :hidden:

   examples/custom-interfaces
   examples/gallery

.. toctree::
   :caption: Reference
   :maxdepth: 3
   :hidden:

   reference
