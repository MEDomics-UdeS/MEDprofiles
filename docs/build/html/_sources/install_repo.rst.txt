##################################################
Use the MEDprofiles package inside this repository
##################################################


The MEDprofiles repository requires *python 3.8* or higher to run.

Install the requirements as following :


``pip install -r requirements.txt``

Additionally, you need to add the data locally. Depending on whether you are working with the Meningioma or MIMIC-IV
dataset, refer to the respective instructions below.


Meningioma dataset
==================

Copy the following files into *data/meningioma/csv* :

- *meningioma.outcome.time004.pathology.csv*
- *meningioma.variable.time001.demographics.csv*
- *meningioma.variable.time002.radiographics.csv*
- *meningioma.variable.time003.therapy.csv*
- *meningioma.variable.time004.pathology.csv*

Next, run *data/meningioma/create_master_table.ipynb*. This will generate the master table used throughout the
repository, saved as *data/meningioma/csv/master_table.csv*.


MIMIC-IV dataset
================

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
`link <https://github.com/EmilyAlsentzer/clinicalBERT>`_.
You need to add the *pretrained_bert_tf* folder under *data/mimic/*. The folder must contain at least a subfolder
*biobert_pretrain_output_all_notes_150000*. Make sure the config *json* file in this subfolder is named *config.json*.

Then, run *data/mimic/create_master_table.ipynb*. This will create the master table used in the repository, saved as
*data/mimic/csv/master_table.csv*. Please note that, for computational efficiency, the master table created for the
MIMIC-IV dataset will only contain a sample of one hundred patients. If you wish to create a master table with more
patients for your study, you can modify the following line in the main function, specifying the desired number of
patients:

``patient_list = random.sample(set(df_embeddings['haim_id']), 100)``