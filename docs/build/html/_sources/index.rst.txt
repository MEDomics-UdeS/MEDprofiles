.. MEDprofiles documentation master file, created by
   sphinx-quickstart on Wed May 10 14:03:01 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MEDprofiles's documentation!
=======================================

This repository contains a Python package for treatment and visualization of patient data. It is a component of
the `MEDomicsLab <https://github.com/MEDomics-UdeS/MEDomicsLab>`_ project. The package is specifically tailored to work
with two datasets: Meningioma and MIMIC-IV. The repository also contains code to demonstrate the use of the MEDprofiles
package.

The MEDprofiles package offers several functionalities, including:

- Dynamically creating classes from a master table, following a certain configuration, allowing for convenient
  manipulation of data as MEDprofiles objects.
- Instantiating data as MEDprofiles objects based on the previously generated classes.
- Displaying and manipulating MEDprofiles objects, either one at a time or by cohort.

These features enable efficient handling and analysis of patient data extracted from the original CSV files.


.. toctree::
   :maxdepth: 1
   :caption: Getting started:

   install_package
   install_repo


.. toctree::
   :maxdepth: 1
   :caption: Tutorials:

   instructions
   notebooks


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   data
   MEDclasses
   backend
   semi_front_classes
   semi_front_utils



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
