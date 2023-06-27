"""

This file create a temporal master table from Meningioma data. The folder meningioma/csv must contains the following csv
files:

- meningioma.outcome.time004.pathology.csv
- meningioma.variable.time001.demographics.csv
- meningioma.variable.time002.radiographics.csv
- meningioma.variable.time003.therapy.csv
- meningioma.variable.time004.pathology.csv

"""
import datetime
import numpy as np
import pandas as pd
import random
import time


def main():
    """
    Main function that creates a temporal master table from Meningioma data.

    :return:

    """
    # Import all csv
    df_demographics_01 = pd.read_csv('csv/meningioma.variable.time001.demographics.csv')
    df_demographics_01['Time_point'] = 1.0
    df_demographics_01['Date'] = ''
    df_radiographics_02 = pd.read_csv('csv/meningioma.variable.time002.radiographics.csv')
    df_radiographics_02['Time_point'] = 2.0
    df_radiographics_02['Date'] = ''
    df_therapy_03 = pd.read_csv('csv/meningioma.variable.time003.therapy.csv')
    df_therapy_03['Time_point'] = 3.0
    df_therapy_03['Date'] = ''
    df_pathology_04 = pd.read_csv('csv/meningioma.variable.time004.pathology.csv')
    df_pathology_04['Time_point'] = 4.0
    df_pathology_04['Date'] = ''
    df_outcome = pd.read_csv('csv/meningioma.outcome.time004.pathology.csv')
    df_outcome['Time_point'] = None

    # Rename csv columns
    col_names = {}
    for element in df_demographics_01.columns:
        if element != 'ID' and element != 'Time_point' and element != 'Date':
            col_names[element] = 'Demographic_' + element.replace('_', '').replace('.', '')
    df_demographics_01 = df_demographics_01.rename(columns=col_names)

    col_names = {}
    for element in df_radiographics_02.columns:
        if element != 'ID' and element != 'Time_point' and element != 'Date':
            col_names[element] = 'Radiographic_' + element.replace('_', '').replace('.', '')
    df_radiographics_02 = df_radiographics_02.rename(columns=col_names)

    col_names = {}
    for element in df_therapy_03.columns:
        if element != 'ID' and element != 'Time_point' and element != 'Date':
            col_names[element] = 'Therapy_' + element.replace('_', '').replace('.', '')
    df_therapy_03 = df_therapy_03.rename(columns=col_names)

    col_names = {}
    for element in df_pathology_04.columns:
        if element != 'ID' and element != 'Time_point' and element != 'Date':
            col_names[element] = 'Pathology_' + element.replace('_', '').replace('.', '')
    df_pathology_04 = df_pathology_04.rename(columns=col_names)

    col_names = {}
    for element in df_outcome.columns:
        if element != 'ID' and element != 'Time_point':
            col_names[element] = 'Event_' + element.replace('_', '').replace('.', '')
    df_outcome = df_outcome.rename(columns=col_names)

    # Events cases
    df_event_localR = pd.DataFrame(df_outcome[['ID', 'Time_point', 'Event_LocalRbinary']])
    df_event_death = pd.DataFrame(df_outcome[['ID', 'Time_point', 'Event_Deathbinary']])

    # Add random dates

    # Define range for 1st time point
    start_date = datetime.date(2010, 1, 1)
    end_date = datetime.date(2022, 12, 31)

    # Week duration in seconds
    week_duration = 604800

    # Month duration in seconds
    month_duration = 2628000

    for id in df_demographics_01.index:
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)

        # Time point 1
        random_date_1 = start_date + datetime.timedelta(days=random_number_of_days)
        timestamp_random_date_1 = time.mktime(random_date_1.timetuple())
        df_demographics_01.at[id, 'Date'] = random_date_1

        # Time point 2
        timestamp_random_date_2 = random.gauss(timestamp_random_date_1 + 2 * week_duration, week_duration)
        random_date_2 = datetime.date.fromtimestamp(timestamp_random_date_2)
        df_radiographics_02.at[id, 'Date'] = random_date_2

        # Time point 3
        timestamp_random_date_3 = random.gauss(timestamp_random_date_2 + 2 * week_duration, week_duration)
        random_date_3 = datetime.date.fromtimestamp(timestamp_random_date_3)
        df_therapy_03.at[id, 'Date'] = random_date_3

        # Time point 4
        timestamp_random_date_4 = random.gauss(timestamp_random_date_3 + 2 * week_duration, week_duration)
        random_date_4 = datetime.date.fromtimestamp(timestamp_random_date_4)
        df_pathology_04.at[id, 'Date'] = random_date_4

        # Event_LocalReventFreeTime
        if not np.isnan(df_outcome.at[id, 'Event_LocalReventFreeTime']):
            df_event_localR.at[id, 'Date'] = datetime.date.fromtimestamp(
                timestamp_random_date_1 + df_outcome.at[id, 'Event_LocalReventFreeTime'] * month_duration)
        else:
            df_event_localR.drop(id, axis=0, inplace=True)

        # Event_DeatheventFreeTime
        if not np.isnan(df_outcome.at[id, 'Event_DeatheventFreeTime']):
            df_event_death.at[id, 'Date'] = datetime.date.fromtimestamp(
                timestamp_random_date_1 + df_outcome.at[id, 'Event_DeatheventFreeTime'] * month_duration)
        else:
            df_event_death.drop(id, axis=0, inplace=True)

    # Fill master_table
    df_master = pd.concat(
        [df_demographics_01, df_radiographics_02, df_therapy_03, df_pathology_04, df_event_localR, df_event_death])
    col = df_master.pop("Time_point")
    df_master.insert(1, col.name, col)
    col = df_master.pop("Date")
    df_master.insert(1, col.name, col)
    df_master = df_master.set_index('ID')
    df_master = df_master.sort_values(['ID', 'Time_point'])

    # Set the master table at the right format

    # Get types of columns
    types = []
    for element in list(df_master.dtypes):
        if element == 'object':
            types.append('str')
        else:
            types.append('num')
    types[0] = 'datetime.date'
    types[1] = 'float'

    # Insert column names in data
    df_col = pd.DataFrame([df_master.columns], columns=list(df_master.columns))
    df_master = pd.concat([df_col, df_master]).rename(index={0: 'PatientID'})

    # Insert columns types in data
    df_types = pd.DataFrame([types], columns=df_master.columns)
    df_master = pd.concat([df_types, df_master]).rename(index={0: 'str'})

    # Save the time_series dataframe into a csv file
    df_master.to_csv('csv/master_table.csv', header=False)


if __name__ == '__main__':
    main()
