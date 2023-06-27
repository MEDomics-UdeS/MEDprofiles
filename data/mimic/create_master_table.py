"""

This file create a temporal master table from MIMIC-IV data. The folder mimic/csv must contains the following csv files:

- admissions.csv
- chartevents.csv
- cxr_ic_fusion_1103.csv
- d_items.csv
- d_labitems.csv
- haim_mimiciv_key_ids.csv
- labevents.csv
- procedureevents.csv
- radiology.csv

"""

# Imports
import datetime
import numpy as np
import pandas as pd
import random
from dask import dataframe as dd
from dask.diagnostics import ProgressBar
from tqdm import tqdm
from scipy.signal import find_peaks
from transformers import AutoTokenizer, AutoModel, logging

ProgressBar().register()
logging.set_verbosity_error()

# Define constants
CHARTEVENTS = ['Heart Rate', 'Non Invasive Blood Pressure systolic',
               'Non Invasive Blood Pressure diastolic', 'Non Invasive Blood Pressure mean',
               'Respiratory Rate', 'O2 saturation pulseoxymetry',
               'GCS - Verbal Response', 'GCS - Eye Opening', 'GCS - Motor Response']
LABEVENTS = ['Glucose', 'Potassium', 'Sodium', 'Chloride', 'Creatinine',
             'Urea Nitrogen', 'Bicarbonate', 'Anion Gap', 'Hemoglobin', 'Hematocrit',
             'Magnesium', 'Platelet Count', 'Phosphate', 'White Blood Cells',
             'Calcium, Total', 'MCH', 'Red Blood Cells', 'MCHC', 'MCV', 'RDW',
             'Platelet Count', 'Neutrophils', 'Vancomycin']
PROCEDUREEVENTS = ['Foley Catheter', 'PICC Line', 'Intubation', 'Peritoneal Dialysis',
                   'Bronchoscopy', 'EEG', 'Dialysis - CRRT', 'Dialysis Catheter',
                   'Chest Tube Removed', 'Hemodialysis']

# Set biobert parameters
BIOBERT_PATH = 'pretrained_bert_tf/biobert_pretrain_output_all_notes_150000/'
BIOBERT_TOKENIZER = AutoTokenizer.from_pretrained(BIOBERT_PATH)
BIOBERT_MODEL = AutoModel.from_pretrained(BIOBERT_PATH)


def get_patient_identifiers(haim_id, df_key_ids):
    """
    Get patient identifiers (ie. subject_id, hadm_id, stay_id) given haim_id.

    :param haim_id: haim_id of the patient we want identifiers.
    :param df_key_ids: Pandas Dataframe from haim_mimic_key_ids.csv.

    :return: Dict of patients identifiers matching haim_id.

    """
    return {'subject_id': df_key_ids.loc[haim_id]['subject_id'], 'hadm_id': df_key_ids.loc[haim_id]['hadm_id'],
            'stay_id': df_key_ids.loc[haim_id]['stay_id']}


def get_patient_id(dict_patient_identifiers, df_key_ids):
    """
    Get patient id from dict of identifiers.

    :param dict_patient_identifiers: Dict of patient identifiers (i.e. subject_id, hadm_id, stay_id).
    :param df_key_ids: Pandas Dataframe from haim_mimic_key_ids.csv.

    :return:

    """
    # Create list to keep order
    list_patient_identifiers = list(dict_patient_identifiers.keys())
    if len(list_patient_identifiers) == 3:
        return df_key_ids[
            (df_key_ids[list_patient_identifiers[0]] == dict_patient_identifiers[list_patient_identifiers[0]]) &
            (df_key_ids[list_patient_identifiers[1]] == dict_patient_identifiers[list_patient_identifiers[1]]) &
            (df_key_ids[list_patient_identifiers[2]] == dict_patient_identifiers[list_patient_identifiers[2]])].index[0]


def filter_df_with_patient_identifiers(df, dict_patient_identifiers):
    """
    Get all data matching the patient identifiers in df.

    :param df: Pandas dataframe.
    :param dict_patient_identifiers: Dict of patient identifiers (i.e. subject_id, hadm_id, stay_id).

    :return: Filtered dataframe.

    """
    # Create a list of identifier given df columns
    list_patient_identifiers = []
    for identifier in dict_patient_identifiers.keys():
        if identifier in df.columns:
            list_patient_identifiers.append(identifier)
    if len(list_patient_identifiers) == 2:
        return df[(df[list_patient_identifiers[0]] == dict_patient_identifiers[list_patient_identifiers[0]]) & (
                df[list_patient_identifiers[1]] == dict_patient_identifiers[list_patient_identifiers[1]])]
    # Here len is supposed to be 3
    return df[(df[list_patient_identifiers[0]] == dict_patient_identifiers[list_patient_identifiers[0]]) & (
            df[list_patient_identifiers[1]] == dict_patient_identifiers[list_patient_identifiers[1]]) & (
                      df[list_patient_identifiers[2]] == dict_patient_identifiers[list_patient_identifiers[2]])]


def get_patient_demographic_embeddings(patient_id, dict_patient_identifiers, df_embeddings, df_admissions):
    """
    Return patient demographic embeddings from df_embeddings and admission time.

    :param patient_id: hadm_id of the patient.
    :param dict_patient_identifiers: Dict of patient identifiers (i.e. subject_id, hadm_id, stay_id).
    :param df_embeddings: Pandas Dataframe from cxr_ic_fusion_1103.csv.
    :param df_admissions: Pandas Dataframe from admissions.csv.

    :return: df_demographic_embeddings: Pandas Dataframe containing demographic embeddings of the considered patient.

    """
    dict_demographic_attributes = {'de_0': 'demographic_anchor_age', 'de_1': 'demographic_gender_int',
                                   'de_2': 'demographic_ethnicity_int', 'de_3': 'demographic_marital_status_int',
                                   'de_4': 'demographic_language_int', 'de_5': 'demographic_insurance_int'}
    df_demographic_embeddings = df_embeddings[df_embeddings['haim_id'] == patient_id][
        list(dict_demographic_attributes.keys())].drop_duplicates()
    df_demographic_embeddings.insert(0, 'PatientID', patient_id)
    admittime = df_admissions[(df_admissions['subject_id'] == dict_patient_identifiers['subject_id']) & (
            df_admissions['hadm_id'] == dict_patient_identifiers['hadm_id'])]['admittime']
    if len(admittime) == 1:
        df_demographic_embeddings.insert(1, 'Date', df_admissions[
            (df_admissions['subject_id'] == dict_patient_identifiers['subject_id']) & (
                    df_admissions['hadm_id'] == dict_patient_identifiers['hadm_id'])]['admittime'].item())
    df_demographic_embeddings.rename(columns=dict_demographic_attributes, inplace=True)
    return df_demographic_embeddings


def generate_event_sr_embeddings(sr_patient_event, event):
    """
    Generate embeddings for an event given time series data.

    :param sr_patient_event: Pandas time series concerning a certain event for a patient.
    :param event: The event name (str).

    :return: sr_embeddings: Embeddings for the series sr_patient_event.

    """
    sr_embeddings = pd.Series()
    if len(sr_patient_event) > 0:
        sr_embeddings[event + '_max'] = sr_patient_event.max()
        sr_embeddings[event + '_min'] = sr_patient_event.min()
        sr_embeddings[event + '_mean'] = sr_patient_event.mean(skipna=True)
        sr_embeddings[event + '_variance'] = sr_patient_event.var(skipna=True)
        sr_embeddings[event + '_meandiff'] = sr_patient_event.diff().mean()
        sr_embeddings[event + '_meanabsdiff'] = sr_patient_event.diff().abs().mean()
        sr_embeddings[event + '_maxdiff'] = sr_patient_event.diff().abs().max()
        sr_embeddings[event + '_sumabsdiff'] = sr_patient_event.diff().abs().sum()
        sr_embeddings[event + '_diff'] = sr_patient_event.iloc[-1] - sr_patient_event.iloc[0]
        # Compute the n_peaks
        peaks, _ = find_peaks(sr_patient_event)
        sr_embeddings[event + '_npeaks'] = len(peaks)
        # Compute the trend (linear slope)
        if len(sr_patient_event) > 1:
            sr_embeddings[event + '_trend'] = np.polyfit(np.arange(len(sr_patient_event)), sr_patient_event, 1)[0]
        else:
            sr_embeddings[event + '_trend'] = 0
    return sr_embeddings


def generate_patient_event_embeddings_between_dates(df_events, event_list, df_item_label, dict_patient_identifiers,
                                                    time_column, series_column, event_category_name, start_date,
                                                    end_date):
    """
    Generate embeddings for events for a patient between 2 dates.

    :param df_events: Pandas Dataframe from event type csv (chartevents, labevents or procedureevents).
    :param event_list: List of event we want to filter (CHARTEVENTS, LABEVENTS, PROCEDUREEVENTS).
    :param df_item_label: Pandas Dataframe from d_items or d_labitems csv.
    :param dict_patient_identifiers: Dict of patient identifiers (i.e. subject_id, hadm_id, stay_id).
    :param time_column: Column associated to time we want to consider in df_events.
    :param series_column: Column associated to series values we want to consider in df_event.
    :param event_category_name: Name we want to give to the event type in the master table.
    :param start_date: Date where we start looking for.
    :param end_date: Date where we stop looking for.

    :return: df_event_embeddings: Generated embeddings for the events in event_list between start_date and end_date.

    """
    # Filter df_events with patient identifiers
    df_events_patient = filter_df_with_patient_identifiers(df_events, dict_patient_identifiers)

    # Filter df_patient with start_date and end_date
    df_events_patient = df_events_patient[
        (df_events_patient[time_column] >= start_date) & (df_events_patient[time_column] < end_date)]

    # Create a dict that associates label to item id
    event_dict = {}
    for event in event_list:
        event_dict[event] = df_item_label[df_item_label['label'] == event]['itemid'].tolist()

    # Generate embeddings for each event
    df_event_embeddings = pd.DataFrame()
    for event in event_dict:
        sr_event = df_events_patient[df_events_patient['itemid'].isin(event_dict[event])][series_column].astype(float)
        event_name = event_category_name + '_' + event.lower().replace(',', '').replace(' -', '').replace(' ', '_')
        sr_embeddings = generate_event_sr_embeddings(sr_event, event_name)
        df_event_embeddings = pd.concat([df_event_embeddings, pd.DataFrame(sr_embeddings).transpose()], axis=1)
    df_event_embeddings.insert(0, 'Date', start_date)

    return df_event_embeddings


def generate_patient_event_embeddings(df_events, event_list, df_item_label, df_key_ids, dict_patient_identifiers,
                                      time_column, series_column, event_category_name, timedelta):
    """
    Generate patient embeddings for a certain event category, one row every timedelta range.

    :param df_events: Pandas Dataframe from event type csv (chartevents, labevents or procedureevents).
    :param event_list: List of event we want to filter (CHARTEVENTS, LABEVENTS, PROCEDUREEVENTS).
    :param df_item_label: Pandas Dataframe from d_items or d_labitems csv.
    :param df_key_ids: Pandas Dataframe from haim_mimic_key_ids.csv.
    :param dict_patient_identifiers: Identifiers in the dataframe which allow to recognize a patient.
    :param time_column: Column associated to time we want to consider in df_events.
    :param series_column: Column associated to series values we want to consider in df_event.
    :param event_category_name: Name we want to give to the event type in the master table.
    :param timedelta: Range to consider getting timeseries.

    :return: df_event_embeddings: Generated embeddings for the events in event list for the considered patient, computed
             at every timedelta range.

    """
    # Filter df_events with patient identifiers
    sr_time_patient = filter_df_with_patient_identifiers(df_events, dict_patient_identifiers)[time_column]

    if len(sr_time_patient) > 0:
        # Get dates range every 24h during patient stay
        start_date = sr_time_patient.iloc[0]
        end_date = start_date + timedelta
        last_date = sr_time_patient.iloc[-1]

        # Create dataframe
        df_event_embeddings = pd.DataFrame()

        # Get embeddings for every 24 hours range
        while start_date <= last_date:
            df_event_embeddings = pd.concat([df_event_embeddings,
                                             generate_patient_event_embeddings_between_dates(df_events, event_list,
                                                                                             df_item_label,
                                                                                             dict_patient_identifiers,
                                                                                             time_column, series_column,
                                                                                             event_category_name,
                                                                                             start_date, end_date)],
                                            ignore_index=True)
            start_date += timedelta
            end_date += timedelta

        # Get patient id
        df_event_embeddings.insert(0, 'PatientID', get_patient_id(dict_patient_identifiers, df_key_ids))
        df_event_embeddings.dropna(subset=df_event_embeddings.columns[2:], how='all', inplace=True)
        return df_event_embeddings


def get_patient_image_and_notes_embeddings(patient_id, df_embeddings):
    """
    Get image and notes embeddings from the embeddings dataframe given a patient_id.

    :param patient_id: hadm_id of a patient.
    :param df_embeddings: Pandas Dataframe from cxr_ic_fusion_1103.csv.

    :return: df_image_embeddings: Image and notes embeddings for the patient.

    """
    columns = ['haim_id', 'img_charttime']
    dict_new_column_names = {'haim_id': 'PatientID', 'img_charttime': 'Date'}

    # Get columns names referring to image embeddings
    for column in df_embeddings.columns:
        if column.startswith('vp_') or column.startswith('vd_') or column.startswith('vmp') or column.startswith('vmd'):
            columns.append(column)
            dict_new_column_names[column] = column.split('_')[0] + '_' + 'attr_' + str(column.split('_')[1])
        elif column.startswith('n_ecg') or column.startswith('n_ech'):
            columns.append(column)
            dict_new_column_names[column] = column.split('_')[0] + column.split('_')[1] + '_' + 'attr_' + str(
                column.split('_')[2])

    # Filter df_embeddings with patient_id
    df_image_embeddings = df_embeddings[df_embeddings['haim_id'] == patient_id][columns]
    df_image_embeddings.rename(columns=dict_new_column_names, inplace=True)

    return df_image_embeddings


def split_note_document(text, min_length=15):
    """
    Function taken from the GitHub repository of the HAIM study. Split a text if too long for embeddings generation.

    :param text: String of text to be processed into an embedding. BioBERT can only process a string with â‰¤ 512 tokens
           . If the input text exceeds this token count, we split it based on line breaks (driven from the discharge
           summary syntax).
    :param min_length: When parsing the text into its subsections, remove text strings below a minimum length. These are
           generally very short and encode minimal information (e.g. 'Name: ___').

    :return: chunk_parse: A list of "chunks", i.e. text strings, that breaks up the original text into strings with 512
             tokens.
             chunk_length: A list of the token counts for each "chunk".

    """
    tokens_list_0 = BIOBERT_TOKENIZER.tokenize(text)

    if len(tokens_list_0) <= 510:
        return [text], [1]

    chunk_parse = []
    chunk_length = []
    chunk = text

    # Go through text and aggregate in groups up to 510 tokens (+ padding)
    tokens_list = BIOBERT_TOKENIZER.tokenize(chunk)
    if len(tokens_list) >= 510:
        temp = chunk.split('\n')
        ind_start = 0
        len_sub = 0
        for i in range(len(temp)):
            temp_tk = BIOBERT_TOKENIZER.tokenize(temp[i])
            if len_sub + len(temp_tk) > 510:
                chunk_parse.append(' '.join(temp[ind_start:i]))
                chunk_length.append(len_sub)
                # reset for next chunk
                ind_start = i
                len_sub = len(temp_tk)
            else:
                len_sub += len(temp_tk)
    elif len(tokens_list) >= min_length:
        chunk_parse.append(chunk)
        chunk_length.append(len(tokens_list))

    return chunk_parse, chunk_length


def get_biobert_embeddings(text):
    """
    Function taken from the GitHub repository of the HAIM study. Obtain BioBERT embeddings of text string.

    :param text: Input text (str).

    :return: embeddings: Final Biobert embeddings with vector dimensionality = (1,768).
             hidden_embeddings: Last hidden layer in Biobert model with vector dimensionality = (token_size,768).

    """
    tokens_pt = BIOBERT_TOKENIZER(text, return_tensors="pt")
    outputs = BIOBERT_MODEL(**tokens_pt)
    last_hidden_state = outputs.last_hidden_state
    pooler_output = outputs.pooler_output
    hidden_embeddings = last_hidden_state.detach().numpy()
    embeddings = pooler_output.detach().numpy()

    return embeddings, hidden_embeddings


def get_biobert_embeddings_from_event_list(event_list, event_weights):
    """
    Function taken from the GitHub repository of the HAIM study. For notes obtain fixed-size BioBERT embeddings.

    :param event_list: Timebound ICU patient stay structure filtered by max_time_stamp or min_time_stamp if any.
    :param event_weights: Weights for aggregation of features in final embeddings.

    :return: aggregated_embeddings: BioBERT event features for all events.

    """
    event_weights_exp = []
    for idx, event_string in enumerate(event_list):
        weight = event_weights.values[idx]
        string_list, lengths = split_note_document(event_string)
        for idx_sub, event_string_sub in enumerate(string_list):
            # Extract biobert embedding
            embedding, hidden_embedding = get_biobert_embeddings(event_string_sub)
            # Concatenate
            if (idx == 0) & (idx_sub == 0):
                full_embedding = embedding
            else:
                full_embedding = np.concatenate((full_embedding, embedding), axis=0)
            event_weights_exp.append(weight)

    # Return the weighted average of embedding vector across temporal dimension
    try:
        aggregated_embedding = np.average(full_embedding, axis=0, weights=np.array(event_weights_exp))
    except:
        aggregated_embedding = np.zeros(768)

    return aggregated_embedding


def generate_patient_notes_embeddings_between_dates(df_notes, df_admissions, dict_patient_identifiers, start_date,
                                                    end_date):
    """
    Generate patient notes embeddings between two dates.

    :param df_notes: Pandas Dataframe from notes.
    :param df_admissions: Pandas Dataframe from admissions.csv.
    :param dict_patient_identifiers: Dict of patient identifiers (i.e. subject_id, hadm_id, stay_id).
    :param start_date: Beginning date to consider for embeddings generation.
    :param end_date: End date to consider for embeddings generation.

    :return: df_patient_notes_embeddings: Pandas Dataframe of note embeddings for the patient matching
             dict_patient_identifiers between start date and end date.

    """
    # Filter df_notes with patient identifiers
    df_notes_patient = filter_df_with_patient_identifiers(df_notes, dict_patient_identifiers)

    # Filter df_patient with start_date and end_date
    df_notes_patient = df_notes_patient[
        (df_notes_patient['charttime'] >= start_date) & (df_notes_patient['charttime'] < end_date)]

    # Get weights for embeddings
    admittime = filter_df_with_patient_identifiers(df_admissions, dict_patient_identifiers)['admittime'].values[0]
    df_notes_patient['deltacharttime'] = df_notes_patient['charttime'].apply(
        lambda x: (x.replace(tzinfo=None) - admittime).total_seconds() / 3600)

    # Call function for embeddings generation
    df_patient_notes_embeddings = pd.DataFrame(
        [get_biobert_embeddings_from_event_list(df_notes_patient['text'], df_notes_patient['deltacharttime'])])
    df_patient_notes_embeddings.insert(0, 'Date', start_date)

    return df_patient_notes_embeddings


def generate_patient_notes_embeddings(df_notes, df_admissions, df_key_ids, patient_id, timedelta):
    """
    Generate notes embeddings for a patient every timedelta range.

    :param df_notes: Pandas Dataframe of notes (radiology.csv).
    :param df_admissions: Pandas Dataframe from admissions.csv.
    :param df_key_ids: Pandas Dataframe from haim_mimic_key_ids.csv.
    :param patient_id: hadm_id of a patient.
    :param timedelta: Time range for embeddings generation.

    :return: df_notes_embeddings: Pandas Dataframe of notes embeddings for the considered patient, every timedelta range

    """
    # Get notes times for a specific patient as series
    patient_identifiers = get_patient_identifiers(patient_id, df_key_ids)
    sr_time_patient = filter_df_with_patient_identifiers(df_notes, patient_identifiers)['charttime']

    if len(sr_time_patient) > 0:
        # Get dates range every 24h during patient stay
        start_date = sr_time_patient.iloc[0]
        end_date = start_date + timedelta
        last_date = sr_time_patient.iloc[-1]

        # Create dataframe
        df_notes_embeddings = pd.DataFrame()

        # Get embeddings for every 24 hours range
        while start_date <= last_date:
            embeddings = generate_patient_notes_embeddings_between_dates(df_notes, df_admissions, patient_identifiers,
                                                                         start_date, end_date)
            df_notes_embeddings = pd.concat([df_notes_embeddings, embeddings], ignore_index=True)
            start_date += timedelta
            end_date += timedelta

        # Rename columns
        col_number = len(df_notes_embeddings.columns) - 1
        df_notes_embeddings.columns = ['Date'] + ['nrad_attr_' + str(i) for i in range(col_number)]

        # Insert patient haim_id in the dataframe
        df_notes_embeddings.insert(0, 'PatientID', patient_id)

        return df_notes_embeddings


def main():
    """
    Main function that creates a temporal master table from MIMIC-IV data.

    :return:

    """
    # Read all csv data
    df_admissions = dd.read_csv('csv/admissions.csv', assume_missing=True,
                                dtype={'admission_location': 'object', 'deathtime': 'object', 'edouttime': 'object',
                                       'edregtime': 'object'})
    df_chart_events = dd.read_csv('csv/chartevents.csv', assume_missing=True, low_memory=False,
                                  dtype={'value': 'object', 'valueuom': 'object'})
    df_embeddings = pd.read_csv('csv/cxr_ic_fusion_1103.csv', on_bad_lines='skip')
    df_items = pd.read_csv('csv/d_items.csv')
    df_key_ids = pd.read_csv('csv/haim_mimiciv_key_ids.csv')
    df_lab_events = dd.read_csv('csv/labevents.csv', assume_missing=True, low_memory=False,
                                dtype={'storetime': 'object', 'value': 'object', 'valueuom': 'object', 'flag': 'object',
                                       'priority': 'object', 'comments': 'object'})
    df_lab_items = pd.read_csv('csv/d_labitems.csv')
    df_procedure_events = dd.read_csv('csv/procedureevents.csv', assume_missing=True,
                                      dtype={'value': 'object', 'secondaryordercategoryname': 'object',
                                             'totalamountuom': 'object'})
    df_radnotes = dd.from_pandas(
        pd.read_csv('csv/radiology.csv', dtype={'charttime': 'object', 'storetime': 'object', 'text': 'object'}),
        chunksize=8)

    # Select only a few patients for data manipulation
    patient_list = random.sample(set(df_embeddings['haim_id']), 100)

    # Create a dictionary that associates haim_id to subject_id, hadm_id and stay_id
    dict_patient_id = {}
    for patient_id in patient_list:
        dict_patient_id[patient_id] = get_patient_identifiers(patient_id, df_key_ids)
    df = dd.from_dict(dict_patient_id, orient='index', npartitions=1)

    # Filter data according to patient list
    df_admissions = df_admissions.merge(df, on=['subject_id', 'hadm_id'], how='inner')
    df_chart_events = df_chart_events.merge(df, on=['subject_id', 'hadm_id', 'stay_id'], how='inner')
    df_embeddings = df_embeddings.loc[df_embeddings['haim_id'].isin(patient_list)]
    df_key_ids = df_key_ids.iloc[patient_list]
    df_lab_events = df_lab_events.merge(df, on=['subject_id', 'hadm_id'], how='inner')
    df_procedure_events = df_procedure_events.merge(df, on=['subject_id', 'hadm_id', 'stay_id'], how='inner')
    df_radnotes = df_radnotes.merge(df, on=['subject_id', 'hadm_id'], how='inner')

    # Convert date columns to datetime format
    df_admissions['admittime'] = dd.to_datetime(df_admissions['admittime'], format='ISO8601')
    df_chart_events['charttime'] = dd.to_datetime(df_chart_events['charttime'], format='ISO8601')
    df_lab_events['charttime'] = dd.to_datetime(df_lab_events['charttime'], format='ISO8601')
    df_procedure_events['starttime'] = dd.to_datetime(df_procedure_events['starttime'], format='ISO8601')
    df_radnotes['charttime'] = dd.to_datetime(df_radnotes['charttime'], format='ISO8601')

    # Sort data
    df_admissions = df_admissions[['subject_id', 'hadm_id', 'admittime']].compute().sort_values(
        by=['subject_id', 'hadm_id', 'admittime'])
    df_chart_events = df_chart_events[
        ['subject_id', 'hadm_id', 'stay_id', 'charttime', 'itemid', 'valuenum']].compute().sort_values(
        by=['subject_id', 'hadm_id', 'stay_id', 'charttime'])
    df_lab_events = df_lab_events[['subject_id', 'hadm_id', 'charttime', 'itemid', 'valuenum']].compute().sort_values(
        by=['subject_id', 'hadm_id', 'charttime'])
    df_procedure_events = df_procedure_events[
        ['subject_id', 'hadm_id', 'stay_id', 'starttime', 'itemid', 'value']].compute().sort_values(
        by=['subject_id', 'hadm_id', 'stay_id', 'starttime'])
    df_radnotes = df_radnotes[['subject_id', 'hadm_id', 'charttime', 'text']].compute().sort_values(
        by=['subject_id', 'hadm_id', 'charttime'])

    df_master = pd.DataFrame()
    # Get data for all patients in patient list
    for patient_id, i in zip(patient_list, tqdm(range(len(patient_list)))):
        patient_identifiers = get_patient_identifiers(patient_id, df_key_ids)
        df_patient_demographic = get_patient_demographic_embeddings(patient_id, patient_identifiers, df_embeddings,
                                                                    df_admissions)
        df_chartevents = generate_patient_event_embeddings(df_chart_events, CHARTEVENTS, df_items, df_key_ids,
                                                           patient_identifiers, 'charttime', 'valuenum', 'chartevent',
                                                           datetime.timedelta(days=1))
        df_labevents = generate_patient_event_embeddings(df_lab_events, LABEVENTS, df_lab_items, df_key_ids,
                                                         patient_identifiers, 'charttime', 'valuenum', 'labevent',
                                                         datetime.timedelta(days=1))
        df_procedureevents = generate_patient_event_embeddings(df_procedure_events, PROCEDUREEVENTS, df_items,
                                                               df_key_ids, patient_identifiers, 'starttime', 'value',
                                                               'procedureevent', datetime.timedelta(days=1))
        df_img_notes_embeddings = get_patient_image_and_notes_embeddings(patient_id, df_embeddings)
        df_rad_notes = generate_patient_notes_embeddings(df_radnotes, df_admissions, df_key_ids, patient_id,
                                                         datetime.timedelta(days=1))
        df_master = pd.concat([df_master, df_patient_demographic, df_chartevents, df_labevents, df_procedureevents,
                               df_img_notes_embeddings, df_rad_notes], ignore_index=True)

    df_master['Date'] = pd.to_datetime(df_master['Date'])
    df_master.sort_values(by=['PatientID', 'Date'], inplace=True)
    df_master.insert(2, 'Time_point', np.NaN)

    # Create a type list to add in the master table
    # All the attributes are numbers except the date
    type_list = ['num' for _ in df_master.columns]
    type_list[1] = 'datetime.date'

    # Add types row to the dataframe
    df_types = pd.DataFrame([type_list], columns=df_master.columns)
    df_master = pd.concat([df_types, df_master]).reset_index(drop=True)

    df_master.to_csv('csv/master_table.csv', index=False)


if __name__ == '__main__':
    main()
