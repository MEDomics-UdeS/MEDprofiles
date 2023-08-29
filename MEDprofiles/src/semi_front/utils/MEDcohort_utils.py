"""

Utils functions for manipulation of MEDcohort figure.

"""

import numpy as np

from MEDprofiles.src.semi_front.utils.MEDprofiles_utils import *
from MEDprofiles.src.back.constant import *

medclasses_module = __import__('MEDclasses')


def display_cohort(axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations, xaxis=[FIXED_COLUMNS[1]]):
    """
    Display a cohort given axes, classes and attributes per classes with type of display by class (compact or complete).

    :param axes: Axes from a MEDcohort plot.
    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.
    :param xaxis: From which abscissa is displayed the data.

    :return:

    """
    for patient_id in set(df_cohort.index):
        points, annotations = display_profile(axes, df_cohort.loc[[patient_id]], classes_attributes_dict, xaxis=xaxis)
        dict_points[patient_id] = points
        dict_annotations[patient_id] = annotations


def select_patient(patient_id, axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations,
                   dict_selected_points, dict_selected_annotations, color='red', xaxis=[FIXED_COLUMNS[1]]):
    """
    Select all data from a patient in the given axes.

    :param patient_id: PatientID of a MEDprofile.
    :param axes: Axes from a MEDcohort plot.
    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.
    :param dict_selected_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in
           Axes and corresponding to the selected points in the plot.
    :param color: Desired color for the selected points.
    :param xaxis: From which abscissa is displayed the data.

    :return:

    """
    # Remove points from plot
    remove_from_plot(dict_points[patient_id])
    remove_from_plot(dict_annotations[patient_id])

    # Remove points and annotations from dicts
    dict_points.pop(patient_id, None)
    dict_annotations.pop(patient_id, None)

    # Add selected points to plot
    points, annotations = display_profile(axes, df_cohort.loc[[patient_id]], classes_attributes_dict, color, xaxis)
    dict_selected_points[patient_id] = points
    dict_selected_annotations[patient_id] = annotations


def deselect_patient(patient_id, axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations,
                     dict_selected_points, dict_selected_annotations, xaxis=[FIXED_COLUMNS[1]]):
    """
    Deselect all data from a patient in the given axes.

    :param patient_id: PatientID of a MEDprofile.
    :param axes: Axes from a MEDcohort plot.
    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.
    :param dict_selected_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in
           Axes and corresponding to the selected points in the plot.
    :param xaxis: From which abscissa is displayed the data.

    :return:

    """
    select_patient(patient_id, axes, df_cohort, classes_attributes_dict, dict_selected_points,
                   dict_selected_annotations,
                   dict_points, dict_annotations, 'black', xaxis)


def display_attributes_values(event, df_cohort):
    """
    Show or hide attributes values from the nearest point of the event.

    :param event: Matplotlib Event object.
    :param df_cohort: Pandas Dataframe of a MEDcohort.

    :return:

    """
    children = []
    for child in event.inaxes.get_children():
        if isinstance(child, mpl.text.Annotation) and child.get_text() not in set(df_cohort.index):
            children.append(child)
    if len(children) > 0:
        child = get_nearest_child(event, children)
        if not child.get_visible():
            child.set_visible(True)
        else:
            child.set_visible(False)


def display_patient_id_and_data(event, axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations,
                                dict_selected_points, dict_selected_annotations, xaxis=[FIXED_COLUMNS[1]]):
    """
    Select or deselect patient's points on the axes.

    :param event: Matplotlib Event object.
    :param axes: Axes from a MEDcohort plot.
    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.
    :param dict_selected_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in
           Axes and corresponding to the selected points in the plot.
    :param xaxis: From which abscissa is displayed the data.

    :return:

    """
    children = []
    for child in event.inaxes.get_children():
        if isinstance(child, mpl.text.Annotation) and child.get_text() in set(df_cohort.index):
            children.append(child)
    if len(children) > 0:
        child = get_nearest_child(event, children)
        patient_id = child.get_text()
        # Case patient is not selected
        if patient_id in dict_annotations.keys():
            # Select the patient (set its points color to red)
            select_patient(child.get_text(), axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations,
                           dict_selected_points, dict_selected_annotations, xaxis=xaxis)
            # Display patient id
            children = []
            for child in event.inaxes.get_children():
                if isinstance(child, mpl.text.Annotation) and child.get_text() in set(df_cohort.index):
                    children.append(child)
            if len(children) > 0:
                child = get_nearest_child(event, children)
                child.set_visible(True)
        # Case patient is selected
        else:
            # Deselect the patient (set its points color to black)
            deselect_patient(child.get_text(), axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations,
                             dict_selected_points, dict_selected_annotations, xaxis=xaxis)
            # Hide patient id annotation
            for annotation in dict_annotations[patient_id]:
                if annotation.get_text() in set(df_cohort.index) and annotation.get_visible():
                    annotation.set_visible(False)


def remove_selected_patients(dict_selected_points, dict_selected_annotations):
    """
    Remove selected patients from plot.

    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.
    :param dict_selected_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in
           Axes and corresponding to the selected points in the plot.

    :return:

    """
    for patient_id in list(dict_selected_points.keys()):
        remove_from_plot(dict_selected_points[patient_id])
        remove_from_plot(dict_selected_annotations[patient_id])
        dict_selected_points.pop(patient_id, None)
        dict_selected_annotations.pop(patient_id, None)


def update_cohort(df_cohort, dict_points, dict_selected_points):
    """
    Update cohort dataframe according to dict_points keys.

    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.

    :return:

    """
    for patient in set(df_cohort.index):
        if patient not in dict_points.keys() and patient not in dict_selected_points.keys():
            df_cohort.drop(patient, inplace=True)


def update_plot_one_dict(axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations, color, xaxis):
    """
    Update plot and dict of points and annotations according to the cohort.

    :param axes: Axes from a MEDcohort plot.
    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.
    :param color: Desired color for the selected points.
    :param xaxis: From which abscissa is displayed the data.

    :return:

    """
    for patient_id in list(dict_points.keys()):
        # Clear plot
        remove_from_plot(dict_points[patient_id])
        remove_from_plot(dict_annotations[patient_id])

        # Clear dict
        dict_points.pop(patient_id, None)
        dict_annotations.pop(patient_id, None)

        # Plot current data
        points, annotations = display_profile(axes, df_cohort.loc[[patient_id]], classes_attributes_dict, color,
                                              xaxis=xaxis)

        # Update dict with current data
        dict_points[patient_id] = points
        dict_annotations[patient_id] = annotations


def update_plot(axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations, dict_selected_points,
                dict_selected_annotations, xaxis):
    """
    Update plot, dict of points and annotations and dict of selected points and selected annotations according to
    cohort.

    :param axes: Axes from a MEDcohort plot.
    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.
    :param dict_selected_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in
           Axes and corresponding to the selected points in the plot.
    :param xaxis: From which abscissa is displayed the data.

    :return:

    """
    update_plot_one_dict(axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations, 'black', xaxis)
    update_plot_one_dict(axes, df_cohort, classes_attributes_dict, dict_selected_points, dict_selected_annotations,
                         'red', xaxis)


def set_time_relative_to_class_in_cohort(df_cohort, cls):
    """
    Set relative time at cls in df_cohort.

    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param cls: Class name of considered class as string.

    :return:

    """
    df_cohort['Date'] = pd.to_datetime(df_cohort['Date'], format=DATE_FORMAT)

    # Get column_names relative to class
    column_names = []
    for attribute in get_class_fields(cls):
        column_names.append(str(cls + '_' + attribute))

    # Set relative date to the first date
    first_date = min(df_cohort.dropna(subset=column_names, how='all')['Date'])

    for patient_id in set(df_cohort.index):
        df_profile = df_cohort.loc[[patient_id]]
        relative_time_difference = min(df_profile.dropna(subset=column_names, how='all')['Date']) - first_date
        df_cohort.loc[patient_id, 'Relative_date'] = df_profile['Date'] - relative_time_difference

    df_cohort['Days_from_relative_date'] = df_cohort['Relative_date'] - first_date
    df_cohort['Days_from_relative_date'] = pd.to_numeric(df_cohort['Days_from_relative_date'].dt.days,
                                                         downcast='integer')


def is_class_associated_to_time_point(class_, dict_class_time_points):
    """
    Return True if class where the event occurs is associated to a time point.

    :param class_: class_ from MEDprofile object.
    :param dict_class_time_points: Dict associating class names to their matching time points.

    :return:

    """
    return class_ in list(dict_class_time_points.keys())


def set_time_point(class_, df_cohort, dict_class_time_points):
    """
    Attribute a time point to a class and update cohort.

    :param class_: Class associated to a MEDprofile object.
    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param dict_class_time_points: Dict associating class names to their matching time points.

    :return:

    """
    # Update dict associating class to time points
    time_point = len(list(dict_class_time_points.keys())) + 1
    dict_class_time_points[class_] = time_point

    # Get column_names relative to class
    column_names = []
    for attribute in get_class_fields(class_):
        column_names.append(str(class_ + '_' + attribute))

    # Update cohort where class has values
    df_cohort.loc[df_cohort[column_names].notna().any(axis=1), FIXED_COLUMNS[2]] = time_point


def remove_time_point(class_, df_cohort, dict_class_time_points):
    """
    Remove the time point attributed to a class, update the superiors time points and update cohort.

    :param class_: class associated to a MEDprofile object.
    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param dict_class_time_points: Dict associating class names to their matching time points.

    :return:

    """
    time_point = dict_class_time_points[class_]

    # Remove associated time point from plot
    df_cohort[FIXED_COLUMNS[2]].replace(time_point, np.NaN, inplace=True)

    # Update dict, cohort and plot marker style for superior time points
    for key in dict_class_time_points:
        if dict_class_time_points[key] > time_point:
            sup_time_point = dict_class_time_points[key]
            dict_class_time_points[key] -= 1
            df_cohort[FIXED_COLUMNS[2]].replace(sup_time_point, sup_time_point - 1, inplace=True)

    # Remove class from dict of class with associated time points
    dict_class_time_points.pop(class_, None)


def center_data_in_cohort(dict_points, dict_selected_points):
    """
    Center plot on current data.

    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.

    :return:

    """
    list_x = []
    for patient_id in dict_points.keys():
        for point in dict_points[patient_id]:
            list_x.append(point.get_offsets().data[0][0])
    for patient_id in dict_selected_points.keys():
        for point in dict_selected_points[patient_id]:
            list_x.append(point.get_offsets().data[0][0])
    distance_to_edge = 10 * (max(list_x) - min(list_x)) / len(list_x)
    plt.xlim(min(list_x) - distance_to_edge, max(list_x) + distance_to_edge)


def update_title(title, dict_points, dict_selected_points):
    """
    Update the figure suptitle.

    :param title: Matplotlib title of a MEDcohort figure.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.

    :return:

    """
    nb_patients = len(dict_points.keys()) + len(dict_selected_points.keys())
    title.set_text(f'MEDCohort composed by {nb_patients} patients')


def get_patient_list_for_class_values_at_date(df_cohort, class_, date):
    """
    Return patient list containing value(s) given a class and a time interval.

    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param class_: Class name of the considered class as string.
    :param date: Date we consider.

    :return: List of PatientID in the cohort matching the date.

    """
    # Get not nan values in dataframe
    for attribute in get_class_fields(class_):
        column_name = str(class_ + '_' + attribute)
    df_cohort_not_na = df_cohort.dropna(subset=[column_name]).copy()

    return list(set(df_cohort_not_na[df_cohort_not_na['bin'] == date].index))


def scatter_bin_points(axes, classes_attributes_dict, data_dict, dict_bin_points, dict_bin_annotations):
    """
    Scatter bin points according to data_dict.

    :param axes: Axes from a MEDcohort plot.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param data_dict: Dict where keys are time intervals and values are list of lists of patients (one list per class).
    :param dict_bin_points: Dict of scatter points representing a bin of patients.
    :param dict_bin_annotations: Dict of annotations representing a bin of patients.

    :return:

    """
    remove_selected_patients(dict_bin_points, dict_bin_annotations)

    for date in data_dict.keys():
        points = []
        annotations = []
        for class_index in range(len(classes_attributes_dict.keys())):
            if len(data_dict[date][class_index]) > 0:
                ann_data = ''
                x = date
                y = 1
                points.append(axes[class_index].scatter(x, y, s=10 * len(data_dict[date][class_index]), color='black',
                                                        marker=MARKERS[-1]))
                for patient_id in range(len(data_dict[date][class_index])):
                    ann_data += data_dict[date][class_index][patient_id] + '\n'
                ann_data = ann_data[:-1]
                annotation = axes[class_index].annotate(ann_data, xy=(x, y), bbox=dict(boxstyle="round4"))
                annotations.append(annotation)
                annotation.set_visible(False)
            dict_bin_points[date] = points
            dict_bin_annotations[date] = annotations


def set_in_bin(df_cohort, classes_attributes_dict, frequency):
    """
    Create data dict given classes and frequency.

    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param frequency: "Month" or "Year" depending if we want to set the bin by month or year.

    :return: data_dict: Dict where keys are time intervals and values are list of lists of patients (one list per class)
    .

    """
    data_dict = {}
    if frequency == 'year':
        df_cohort['bin'] = pd.to_datetime(df_cohort[FIXED_COLUMNS[1]]).dt.year
    elif frequency == 'month':
        df_cohort['bin'] = pd.to_datetime(pd.to_datetime(df_cohort[FIXED_COLUMNS[1]]).dt.strftime('%Y-%m'),
                                          format="%Y-%m")
    else:
        return

    for date in df_cohort['bin']:
        data_dict[date] = []
        for class_ in classes_attributes_dict.keys():
            data_dict[date].append(get_patient_list_for_class_values_at_date(df_cohort, class_, date))
    return data_dict


def delete_pressed(dict_points, dict_selected_points, dict_selected_annotations, title):
    """
    Delete selected patients and update figure title.

    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.
    :param dict_selected_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in
           Axes and corresponding to the selected points in the plot.
    :param title: Matplotlib title of a MEDcohort figure.

    :return:

    """
    remove_selected_patients(dict_selected_points, dict_selected_annotations)
    update_title(title, dict_points, dict_selected_points)


def r_pressed(event, axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations, dict_selected_points,
              dict_selected_annotations, xaxis):
    """
    Set relative time at the class matching the axis in which the event occurs. If time is already relative to the
    class, set absolute time.
    If there isn't time point notion (ie every data is at the same date) we set time relative to the data point selected
    . If the class contains points at different time for at least one patient, the relative time is set to the nearest
    point from the event.

    :param event: Matplotlib Event object.
    :param axes: Axes from a MEDcohort plot.
    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.
    :param dict_selected_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in
           Axes and corresponding to the selected points in the plot.
    :param xaxis: From which abscissa is displayed the data.

    :return:

    """
    cls = get_class(event)

    # If time is already relative we set absolute time
    if is_time_relative_to_selected_class(event, xaxis, df_cohort):
        xaxis.append(FIXED_COLUMNS[1])
        xaxis.pop(0)
        axes[0].xaxis.set_major_formatter(mpl.dates.DateFormatter(DATE_FORMAT))
        plt.xlabel('Date', fontsize=12)

    # Cases time isn't relative
    else:
        set_time_relative_to_class_in_cohort(df_cohort, cls)
        xaxis.append('Days_from_relative_date')
        xaxis.pop(0)
        axes[0].xaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
        plt.xlabel('Days from relative time', fontsize=12)

    # Update and re-center the plot
    update_plot(axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations, dict_selected_points,
                dict_selected_annotations, xaxis)
    center_data_in_cohort(dict_points, dict_selected_points)


def t_pressed(event, axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations, dict_selected_points,
              dict_selected_annotations, xaxis, dict_class_time_points, legend_points, fig):
    """
    Set time points according to the class matching the event place.

    :param event: Matplotlib Event object.
    :param axes: Axes from a MEDcohort plot.
    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.
    :param dict_selected_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in
           Axes and corresponding to the selected points in the plot.
    :param xaxis: From which abscissa is displayed the data.
    :param dict_class_time_points: Dict associating class names to their matching time points.
    :param legend_points: Legend of a MEDcohort figure.
    :param fig: A MEDcohort figure.

    :return:

    """
    class_ = get_class(event)
    if not class_:
        return
    if is_class_associated_to_time_point(class_, dict_class_time_points):
        remove_time_point(class_, df_cohort, dict_class_time_points)
    else:
        set_time_point(class_, df_cohort, dict_class_time_points)
    while len(legend_points) > 0:
        remove_from_plot(legend_points[0])
        legend_points.pop(0)
    legend_points.append(set_legend(fig, df_cohort))
    update_plot(axes, df_cohort, classes_attributes_dict, dict_points, dict_annotations, dict_selected_points,
                dict_selected_annotations, xaxis)

'''
def bin_pressed(df_cohort, classes_attributes_dict, frequency, subplot_height, plot_width, colors, dict_bin_points,
                dict_bin_annotations, button_pressed_function):
    """
    Create bin figure according to frequency.

    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param frequency: "Month" or "Year" depending on the frequency we want to use to create bins.
    :param subplot_height: Desired subplot height for the bin figure.
    :param plot_width: Desired plot width for the bin figure.
    :param colors: A list of colors, with at least one per class to display.
    :param dict_bin_points: Dict of scatter points representing a bin of patients.
    :param dict_bin_annotations: Dict of annotations representing a bin of patients.
    :param button_pressed_function: Function associated to the "button_pressed" matplotlib event.

    :return:

    """
    compact_dict = {}
    for cls in classes_attributes_dict:
        compact_dict[cls] = ([], 'compact')
    data_dict = set_in_bin(df_cohort, compact_dict, frequency)
    fig_bin, axes_bin = set_plot(subplot_height, plot_width, compact_dict, colors)
    scatter_bin_points(axes_bin, compact_dict, data_dict, dict_bin_points, dict_bin_annotations)
    fig_bin.canvas.mpl_connect('button_press_event', button_pressed_function)
    fig_bin.suptitle(f'MEDcohort in bin ({frequency}) composed by {len(set(df_cohort.index))} patients', fontsize=16)
'''
'''
def p_pressed(df_cohort, classes_attributes_dict, subplot_height, plot_width, xaxis, colors, dict_selected_points,
              dict_figure_profile, button_pressed_func, key_pressed_func, close_func):
    """
    Called when p is pressed on cohort figure.
    Create profile figures from selected points.

    :param df_cohort: Pandas Dataframe of a MEDcohort.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param subplot_height: Desired subplot height for the bin figure.
    :param plot_width: Desired plot width for the bin figure.
    :param xaxis: From which abscissa is displayed the data.
    :param colors: A list of colors, with at least one per class to display.
    :param dict_selected_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes and
           corresponding to the selected points in the plot.
    :param dict_figure_profile: Dict associating MEDprofiles PatientID to their figure.
    :param button_pressed_func: Function associated to the "button_pressed" matplotlib event.
    :param key_pressed_func: Function associated to the "key_pressed" matplotlib event.
    :param close_func: Function associated to the "close_event" matplotlib event.

    :return:

    """
    for patient_id in dict_selected_points.keys():
        df_profile = df_cohort.loc[[patient_id]].copy()
        fig_profile, axes_profile = set_plot(subplot_height, plot_width, classes_attributes_dict, colors)
        points, annotations = display_profile(axes_profile, df_profile, classes_attributes_dict)
        dict_figure_profile[plt.gcf().number] = (patient_id,
                                                 {'profile_df': df_profile, 'profile_points': {patient_id: points},
                                                  'profile_annotations': {patient_id: annotations},
                                                  'profile_axes': axes_profile, 'profile_xaxis': xaxis.copy()})
        fig_profile.canvas.mpl_connect('button_press_event', button_pressed_func)
        fig_profile.canvas.mpl_connect('key_press_event', key_pressed_func)
        fig_profile.canvas.mpl_connect('close_event', close_func)
        fig_profile.suptitle(f'MEDprofile of patient {patient_id}', fontsize=16)
'''
