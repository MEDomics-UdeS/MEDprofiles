## Table of contents

* [Introduction](#1-introduction)
* [Installation](#2-installation)
* [How to use the repository](#3-how-to-use-the-repository)
* [Documentation](#4-documentation)
* [Datasource's](#5-datasources)
* [Project Tree](#project-tree)


## 1. Introduction

This repository contains a Python package for treatment and visualization of patient data. It is a component of
the [MEDomicsLab](https://github.com/MEDomics-UdeS/MEDomicsLab) project. The package is specifically tailored to work
with two datasets: Meningioma and MIMIC-IV. The repository also contains code to demonstrate the use of the MEDprofiles
package.

The MEDprofiles package offers several functionalities, including:

- Dynamically creating classes from a master table, following a certain configuration, allowing for convenient 
  manipulation of data as MEDprofiles objects.
- Instantiating data as MEDprofiles objects based on the previously generated classes.
- Displaying and manipulating MEDprofiles objects, either one at a time or by cohort.

These features enable efficient handling and analysis of patient data extracted from the original CSV files.


## 2. Installation

### MEDprofiles package

If you want to import the MEDprofiles package in another project, you may install it using the following command at the 
root of your project :

```
pip install git+https://github.com/MEDomics-UdeS/MEDprofiles.git
```

### MEDprofiles repository

The MEDprofiles repository requires *python 3.8* or higher to run.

Install the requirements as following :

```
pip install -r requirements.txt
```

Additionally, you need to add the data locally. Depending on whether you are working with the Meningioma or MIMIC-IV 
dataset, refer to the respective instructions below.

#### Meningioma dataset

Copy the following files into *data/meningioma/csv* :

- *meningioma.outcome.time004.pathology.csv*
- *meningioma.variable.time001.demographics.csv*
- *meningioma.variable.time002.radiographics.csv*
- *meningioma.variable.time003.therapy.csv*
- *meningioma.variable.time004.pathology.csv*

Next, run *data/meningioma/create_master_table.ipynb*. This will generate the master table used throughout the 
repository, saved as *data/meningioma/csv/master_table.csv*.

#### MIMIC-IV dataset

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
*biobert_pretrain_output_all_notes_150000*. Make sure the config *json* file in this subfolder is named *config.json*.

Then, run *data/mimic/create_master_table.ipynb*. This will create the master table used in the repository, saved as 
*data/mimic/csv/master_table.csv*. Please note that, for computational efficiency, the master table created for the 
MIMIC-IV dataset will only contain a sample of one hundred patients. If you wish to create a master table with more 
patients for your study, you can modify the following line in the main function, specifying the desired number of 
patients:

```
# Select only a few patients for data manipulation
patient_list = random.sample(set(df_embeddings['haim_id']), 100)
```


## 3. How to use the repository

To use the repository, follow these steps:

1. **Create the master table**: Start by running the *create_master_table.ipynb* file located in the folder 
   corresponding to the dataset you wish to use.

2. **Instantiate the master table data as MEDprofiles**: Follow the *notebooks/initialize_MEDprofiles_from_mimic_data.ipynb*
   file instructions. This notebook illustrate the process with the mimic data. You may need to make some adjustments if 
   you work with the meningioma dataset. At the end of the execution you must have a MEDclasses folder created at the 
   root of your project and a binary file containing MEDprofiles data located at *data/mimic/MEDprofiles_bin*.

3. **Display and manipulate a MEDprofile figure**: Follow the *notebooks/display_MEDprofile_figure.ipynb* file
   instructions.

4. **Display, manipulate and generate static CSV files from a MEDcohort figure**: Follow the 
   *notebooks/display_MEDcohort_figure_and_generate_static_csv.ipynb* file instructions. At the end of the execution
   you must have generated static csv files under the *output/* folder.


## 4. Documentation

The documentation has been generated using Sphinx. To view it, open the *index.html* file located at 
*docs/build/html/index.html*.


## 5. Datasource's

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
|--- MEDprofiles                        <- The MEDprofiles package
|       |--- MEDclasses                 <- Contains classes related to the package and the dataset
|       |       |--- MEDbaseObject.py   <- Definition of a MEDbaseObject with utility functions (other classes inherit from this class)
|       |       |--- MEDcohort.py       <- Definition of a MEDcohort object composed of a list of MEDprofiles
|       |       |--- MEDprofile.py      <- Definition of a MEDprofile object composed of a list of MEDtabs
|       |       |--- MEDtab.py          <- Definition of a MEDtab object composed of a date and an instance of each class generated by the code depending on the dataset
|       |--- src
|               |--- back
|               |       |--- constant.py                            <- Definition of constants
|               |       |--- create_classes_from_master_table.py    <- Script for MEDclasses generation
|               |       |--- instantiate_data_from_master_table.py  <- Script for the master table data instantiation as MEDprofiles objects
|               |--- semi_front
|                       |--- utils                  <- Folder containing utils functions for interactive figure creation and manipulation
|                       |--- BinFigure.py           <- Class representing a bin figure
|                       |--- MEDcohortFigure.py     <- Class representing a MEDcohort figure
|                       |--- MEDprofileFigure.py    <- Class representing a MEDprofile figure
|
|--- notebooks      <- Tutorials showing how to use the MEDprofiles package
|
|--- output         <- Folder where the CSV files from the final cohort will be generated
```