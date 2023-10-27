"""

Take a master table as entry and instantiate the data.
The file 'create_classes_from_master_table' must have been executed before run.

"""

import datetime

import pandas as pd
import pickle
from tqdm import tqdm

from .constant import *


def main(source_file, destination_file):
    """
    Instantiate a list of MEDPatient objects from a csv file in MEDPatientData file with pickle.

    :param source_file: path to master table file
    :param destination_file: path to the generated pickle file

    """
    medclasses_module = __import__('MEDclasses')

    # Get value from the master table
    df = pd.read_csv(source_file, header=None, low_memory=False)
    df.columns = df.iloc[INDEX_ATTRIBUTE_ROW]
    df = df.drop(INDEX_TYPE_ROW).drop(INDEX_ATTRIBUTE_ROW)

    # Get all the patient id and create an empty list for MEDPatients (reduced for mimic data)
    patient_id_list = df.transpose().loc[FIXED_COLUMNS[0]].drop_duplicates()[:100]
    med_profile_list = []

    # Get data for each MEDPatient
    for patientID, i in zip(patient_id_list, tqdm(range(len(patient_id_list)))):
        # To set dynamically the required attributes (without knowing their names), we have to pass through a dictionary
        init = {FIXED_COLUMNS[0]: patientID}
        med_profile = medclasses_module.MEDprofile(**init)
        profile_data = df.where(df[FIXED_COLUMNS[0]] == patientID).dropna(how='all')
        med_tab_list = []

        # Create MEDTab object for each row
        for row in range(len(profile_data)):
            med_tab = medclasses_module.MEDtab()

            # For each attribute of MEDTab class
            for field in med_tab.__dict__:

                # Fixed attributes are just str or float
                if field in FIXED_COLUMNS:
                    if med_tab.__fields__[field].type_ == datetime.date or med_tab.__fields__[field].type_ == \
                            datetime.datetime:
                        med_tab.__setattr__(field, med_tab.parse_date(profile_data[field].iloc[row]))
                    else:
                        med_tab.__setattr__(field, med_tab.__fields__[field].type_(profile_data[field].iloc[row]))

                # Other attributes are class objects
                else:
                    class_object = medclasses_module.__dict__[field]()

                    for attribute in class_object.__dict__:
                        # Class attributes follow the naming convention "className_attributeName"
                        if str(field + '_' + attribute) in profile_data.columns:
                            null = profile_data[field + '_' + attribute].isnull().iloc[row]
                            if not null:
                                # Set the attribute with the good type
                                class_object.__setattr__(attribute, class_object.__fields__[attribute].type_(
                                    profile_data[field + '_' + attribute].iloc[row]))

                    med_tab.__setattr__(field, class_object)
            med_tab_list.append(med_tab)

        # MEDProfile is composed by a list of MEDTab
        med_profile.__setattr__('list_MEDtab', med_tab_list)
        med_profile_list.append(med_profile)

    # Serialize data
    data_file = open(destination_file, 'ab')
    pickle.dump(med_profile_list, data_file)
    data_file.close()
