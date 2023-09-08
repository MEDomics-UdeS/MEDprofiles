############
Instructions
############

To use the repository, follow these steps:


1. Create the master table
==========================

Start by running the *create_master_table.ipynb* file located in the folder corresponding to the dataset you wish to use.


2. Instantiate the master table data as MEDprofiles
===================================================

Follow the *notebooks/initialize_MEDprofiles_from_mimic_data.ipynb* file instructions. This notebook illustrate the process with the mimic data. You may need to make some adjustments if you work with the meningioma dataset. At the end of the execution you must have a MEDclasses folder created at the root of your project and a binary file containing MEDprofiles data located at *data/mimic/MEDprofiles_bin*.



3. Display and manipulate a MEDprofile figure
=============================================

Follow the *notebooks/display_MEDprofile_figure.ipynb* file instructions.


4. Display, manipulate and generate static CSV files from a MEDcohort figure
============================================================================

Follow the *notebooks/display_MEDcohort_figure_and_generate_static_csv.ipynb* file instructions. At the end of the execution you must have generated static csv files under the *output/* folder.
