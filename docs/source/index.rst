.. MEDprofiles documentation master file, created by
   sphinx-quickstart on Wed May 10 14:03:01 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MEDprofiles's documentation!
=======================================

This is a Python module for treatment and visualization of patient data. It is a component of
the `MEDomicsLab <https://github.com/MEDomics-UdeS/MEDomicsLab>`_ project. The module is specifically tailored to work
with two datasets: Meningioma and MIMIC-IV.

The MEDprofiles module offers several functionalities, including:

- Generating a temporal master table based on a predefined template.
- Dynamically creating classes from the master table, allowing for convenient manipulation of data as MEDprofiles
  objects.
- Instantiating data as MEDprofiles objects based on the previously generated classes.
- Displaying and manipulating MEDprofiles objects, either one at a time or by cohort.

These features enable efficient handling and analysis of patient data extracted from the original CSV files.


.. toctree::
   :maxdepth: 1
   :caption: Getting started:

   installation
   meningioma_dataset
   mimic_dataset


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
   semi_front



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
