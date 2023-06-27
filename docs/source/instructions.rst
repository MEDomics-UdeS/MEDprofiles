############
Instructions
############

To use the package, follow these steps:

1. Create the master table
==========================

Start by running the *create_master_table.ipynb* file located in the folder corresponding to the dataset you wish to use.


2. Specify the constants
========================

Open the *src/back/constant.py* file and comment/uncomment the lines that correspond to your dataset. This step helps in setting the appropriate constants.


3. Create the classes matching your master table
================================================

Run the main function in the *src/back/create_classes_from_master_table.py* file, providing the path to the master table file as a parameter.

- For the Meningioma dataset, the file location is *../../data/meningioma/csv/master_table.csv*.
- For the MIMIC-IV dataset, the file location is *../../data/mimic/csv/master_table.csv*.

The classes will be created under the MEDclasses folder. Initially, the folder contains definitions for four classes:

- MEDbaseObject
- MEDcohort
- MEDprofile
- MEDtab

Ensure that the MEDtab definition is empty (i.e., contains only "pass") because the creation of classes will modify and complete the MEDtab attributes.


4. Instantiate the master table data as MEDprofiles objects
===========================================================

Run the main function in the *src/back/instantiate_data_from_master_table.py* file, providing the path to the master table (*source_file*) and the path for the generated binary file (*destination_file*).

- For the Meningioma dataset:

    - The *source_file* is *../../data/meningioma/csv/master_table.csv*.
    - The *destination_file* is *../../data/meningioma/MEDprofileData*.

- For the MIMIC-IV dataset:

     - The *source_file* is *../../data/mimic/csv/master_table.csv*.
     - The *destination_file* is *../../data/mimic/MEDprofileData*.


5. Once you have completed these steps
======================================

You can visualize your datasets as MEDprofiles by following the notebooks tutorials.
