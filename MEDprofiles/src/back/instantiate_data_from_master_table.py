"""

Take a master table as entry and instantiate the data.
The file 'create_classes_from_master_table' must have been executed before run.

"""

import datetime
import typing

import pandas as pd
import pickle
from tqdm import tqdm

from .constant import *

progress = 0

def get_progress():
    """
    Return the progress of the main function.
    """
    global progress
    return progress


def get_patient_id_list(master_table_path):
    """
    Get all the patients identifiers as list.

    :param master_table_path: path to master table file

    Return patient_id_list
    
    """
    # Get value from the master table
    df = pd.read_csv(master_table_path, header=None, low_memory=False)
    df.columns = df.iloc[INDEX_ATTRIBUTE_ROW]
    df = df.drop(INDEX_TYPE_ROW).drop(INDEX_ATTRIBUTE_ROW)

    # Get all the patient id
    patient_id_list = list(df.transpose().loc[FIXED_COLUMNS[0]].drop_duplicates())
    return patient_id_list


def main(source_file, destination_file, patient_id_list=[]):
    """
    Instantiate a list of MEDPatient objects from a csv file in MEDPatientData file with pickle
    and the list of patient we want to get data from.

    :param source_file: path to master table file
    :param destination_file: path to the generated pickle file

    """

    import MEDclasses as medclasses_module
    global progress
    progress = 0

    # Get value from the master table
    df = pd.read_csv(source_file, header=None, low_memory=False)
    df.columns = df.iloc[INDEX_ATTRIBUTE_ROW]
    df = df.drop(INDEX_TYPE_ROW).drop(INDEX_ATTRIBUTE_ROW)

    # Get all the patient id and create an empty list for MEDPatients
    if len(patient_id_list) == 0:
        patient_id_list = df.transpose().loc[FIXED_COLUMNS[0]].drop_duplicates()
    med_profile_list = []

    # Get data for each MEDPatient
    for patientID, i in zip(patient_id_list, tqdm(range(len(patient_id_list)))):
        # To set dynamically the required attributes (without knowing their names), we have to pass through a dictionary
        init = {FIXED_COLUMNS[0]: patientID}
        med_profile = medclasses_module.MEDprofile(**init)
        profile_data = df.loc[df[FIXED_COLUMNS[0]] == patientID].dropna(how='all')
        med_tab_list = []

        # Create MEDTab object for each row
        for row in range(len(profile_data)):
            med_tab = medclasses_module.MEDtab()

            # For each attribute of MEDTab class
            for field in med_tab.__dict__:

                # Fixed attributes are just str or float
                if field in FIXED_COLUMNS:
                    if str(typing.get_type_hints(med_tab)[field]).__contains__("datetime.date") or str(typing.get_type_hints(med_tab)[field]).__contains__("datetime.datetime"):
                        med_tab.__setattr__(field, med_tab.parse_date(profile_data[field].iloc[row]))
                    else:
                        med_tab.__setattr__(field, profile_data[field].iloc[row])

                # Other attributes are class objects
                else:
                    class_object = medclasses_module.__dict__[field]()

                    for attribute in class_object.__dict__:
                        # Class attributes follow the naming convention "className_attributeName"
                        if str(field + '_' + attribute) in profile_data.columns:
                            null = profile_data[field + '_' + attribute].isnull().iloc[row]
                            if not null:
                                # Set the attribute with the good type
                                class_object.__setattr__(attribute, profile_data[field + '_' + attribute].iloc[row])

                    med_tab.__setattr__(field, class_object)
            med_tab_list.append(med_tab)

        # MEDProfile is composed by a list of MEDTab
        med_profile.__setattr__('list_MEDtab', med_tab_list)
        med_profile_list.append(med_profile)
        progress += 1/len(patient_id_list) * 100

    # Serialize data
    data_file = open(destination_file, 'ab')
    pickle.dump(med_profile_list, data_file)
    data_file.close()
