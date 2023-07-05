## Table of contents

* [Introduction](#1-introduction)
* [Installation](#2-installation)
* [How to use the package](#3-how-to-use-the-package)
* [Documentation](#4-documentation)
* [Tutorials](#5-tutorials)
* [Datasource's](#6-datasources)
* [Project Tree](#project-tree)


## 1. Introduction

This is a Python module for treatment and visualization of patient data. It is a component of
the [MEDomicsLab](https://github.com/MEDomics-UdeS/MEDomicsLab) project. The module is specifically tailored to work
with two datasets: Meningioma and MIMIC-IV.

The MEDprofiles module offers several functionalities, including:

- Generating a temporal master table based on a predefined template.
- Dynamically creating classes from the master table, allowing for convenient manipulation of data as MEDprofiles
  objects.
- Instantiating data as MEDprofiles objects based on the previously generated classes.
- Displaying and manipulating MEDprofiles objects, either one at a time or by cohort.

These features enable efficient handling and analysis of patient data extracted from the original CSV files.


## 2. Installation

The MEDprofile module requires *python 3.8* or higher to run.

Install the requirements as following :

```
pip install -r requirements.txt
```

Additionally, you need to add the data locally. Depending on whether you are working with the Meningioma or MIMIC-IV 
dataset, refer to the respective instructions below.

### Meningioma dataset

Copy the following files into *data/meningioma/csv* :

- *meningioma.outcome.time004.pathology.csv*
- *meningioma.variable.time001.demographics.csv*
- *meningioma.variable.time002.radiographics.csv*
- *meningioma.variable.time003.therapy.csv*
- *meningioma.variable.time004.pathology.csv*

Next, run *data/meningioma/create_master_table.ipynb*. This will generate the master table used throughout the 
repository, saved as *data/meningioma/csv/master_table.csv*.

### MIMIC-IV dataset

Copy the following files into *data/mimic/csv* :

- *admissions.csv*
- *chartevents.csv*
- *cxr_ic_fusion_1103.csv*
- *d_items.csv*
- *d_labitems.csv*
- *haim_mimiciv_key_ids.csv*
- *labevents.csv*
- *procedureevents.csv*
- *radiology.csv*

In order to generate note embeddings, you also need to add pre-trained biomedical language representation model for 
biomedical text mining called BioBERT to the project. You can obtain the BioBERT sources from the following 
[link](https://github.com/EmilyAlsentzer/clinicalBERT). 
You need to add the *pretrained_bert_tf* folder under *data/mimic/*. The folder must contain at least a subfolder 
*biobert_pretrain_output_all_notes_150000*. Make sure the config json file in this subfolder is named config.json.

Then, run *data/mimic/create_master_table.ipynb*. This will create the master table used in the repository, saved as 
*data/mimic/csv/master_table.csv*. Please note that, for computational efficiency, the master table created for the 
MIMIC-IV dataset will only contain a sample of one hundred patients. If you wish to create a master table with more 
patients for your study, you can modify the following line in the main function, specifying the desired number of 
patients:

```
# Select only a few patients for data manipulation
patient_list = random.sample(set(df_embeddings['haim_id']), 100)
```


## 3. How to use the package

To use the package, follow these steps:

1. **Create the master table**: Start by running the *create_master_table.ipynb* file located in the folder 
   corresponding to the dataset you wish to use.

2. **Specify the constants**: Open the *src/back/constant.py* file and comment/uncomment the lines that correspond to 
   your dataset. This step helps in setting the appropriate constants.

3. **Create the classes matching your master table**: Run the main function in the 
   *src/back/create_classes_from_master_table.py* file, providing the path to the master table file as a parameter.
   - For the Meningioma dataset, the file location is *../../data/meningioma/csv/master_table.csv*.
   - For the MIMIC-IV dataset, the file location is *../../data/mimic/csv/master_table.csv*.
   The classes will be created under the MEDclasses folder. Initially, the folder contains definitions for four classes:
   - MEDbaseObject
   - MEDcohort
   - MEDprofile
   - MEDtab

   Ensure that the MEDtab definition is empty (i.e., contains only "pass") because the creation of classes will modify 
   and complete the MEDtab attributes.

4. **Instantiate the master table data as MEDprofile objects**: Run the main function in the 
   *src/back/instantiate_data_from_master_table.py* file, providing the path to the master table (*source_file*) and the
   path for the generated binary file (*destination_file*).
   - For the Meningioma dataset:
     - The *source_file* is *../../data/meningioma/csv/master_table.csv*.
     - The *destination_file* is *../../data/meningioma/MEDprofileData*.
   - For the MIMIC-IV dataset:
     - The *source_file* is *../../data/mimic/csv/master_table.csv*.
     - The *destination_file* is *../../data/mimic/MEDprofileData*.

5. Once you have completed these steps, you can visualize your datasets as MEDprofiles by following the notebook 
   tutorials. For more information, refer to the [Tutorials](#5-tutorials) section.


## 4. Documentation

The documentation has been generated using Sphinx. To view it, open the *index.html* file located at 
*docs/build/html/index.html*.


## 5. Tutorials

All the tutorials are illustrated with MIMIC-IV data but can easily be adapted for Meningioma data. To adapt the 
tutorials for Meningioma data, modify the path to the binary file used for MEDprofiles instantiation and adjust the 
display according to the classes you want to visualize in your MEDprofiles.

The tutorials are available in the following Jupyter Notebooks located in the *notebook* folder:

- *MEDprofiles_visualisation.ipynb*: This tutorial demonstrates how to filter data using the MEDbaseObject, MEDprofile, 
  and MEDcohort functions.
- *MEDprofiles_semi_front.ipynb*: This tutorial shows how to visualize and manipulate a MEDprofile in a matplotlib 
  figure.
- *MEDcohort_semi_front.ipynb*: This tutorial demonstrates how to visualize and manipulate a MEDcohort (a set of 
  MEDprofiles) in a matplotlib figure. Additionally, you will be able to save the cohort data split by time point under 
  the *output/* folder by executing the last cell of the notebook.


## 6. Datasource's

The two datasets used with this repository are confidential data. The Meningioma dataset is available in the MEDomicsLab 
drive folder. The MIMIC-IV dataset is available on [physionet](https://physionet.org/content/mimiciv/2.2/).


## Project Tree

```
|--- data                         <- Contains CSV files from the considered datasets
|     |--- meningioma             <- Contains CSV files for the Meningioma dataset and Python file for master table creation
|     |--- mimic                  <- Contains CSV files for the MIMIC-IV dataset and Python file for master table creation
|
|--- docs                         <- Documentation files autogenerated by Sphinx
|    |--- build/html/index.html   <- Access to the index page of the MEDprofiles package documentation
|
|--- MEDclasses                   <- Contains classes related to the package and the dataset
|    |--- MEDbaseObject.py        <- Definition of a MEDbaseObject with utility functions (other classes inherit from this class)
|    |--- MEDcohort.py            <- Definition of a MEDcohort object composed of a list of MEDprofiles
|    |--- MEDprofile.py           <- Definition of a MEDprofile object composed of a list of MEDtabs
|    |--- MEDtab.py               <- Definition of a MEDtab object composed of a date and an instance of each class generated by the code depending on the dataset
|
|--- notebooks                    <- Tutorials applied to the MIMIC-IV dataset
|
|--- src                          <- Source code for the package
|    |--- back                    <- Constants definition, files for class creation, and data instantiation
|    |--- semi_front              <- Definition of utility functions for profile and cohort display

```