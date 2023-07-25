"""

Utils functions for manipulation of MEDprofile figure.

"""

import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from MEDclasses import *
from src.back.constant import FIXED_COLUMNS, MARKERS, DATE_FORMAT


def get_nb_rows(classes_attributes_dict):
    """
    Count number of rows necessary to plot the figure.

    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.

    :return: nb_row : Number of row in the graphic according to classes_attributes_dict.

    """
    nb_row = 0
    for cls in classes_attributes_dict.keys():
        if classes_attributes_dict[cls][1] == 'compact':
            nb_row += 1
        elif classes_attributes_dict[cls][1] == 'complete':
            if len(classes_attributes_dict[cls][0]) == 0:
                nb_row += len(eval(cls).__fields__)
            else:
                nb_row += len(classes_attributes_dict[cls][0])
    return nb_row


def set_plot(subplot_height, plot_width, classes_attributes_dict, colors):
    """
    Set plots and sublopts with table names and colors to display profile.

    :param subplot_height: Desired height for each subplot.
    :param plot_width: Desired width for the plot.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param colors: List of colors, there is at least one color per class.

    :return: fig, axes: Elements of the created plot.

    """
    nb_row = get_nb_rows(classes_attributes_dict)

    fig, axes = plt.subplots(nb_row, 1, sharex=True, figsize=(plot_width, subplot_height * nb_row))
    fig.subplots_adjust(hspace=0, left=0.2)

    row_index = 0
    classes = list(classes_attributes_dict.keys())
    classes.sort()

    for cls_index, cls in enumerate(classes):
        # If there is no attribute specified in the classes_attributes_dict it means we consider all the attributes
        # so we change that in the dict
        if len(classes_attributes_dict[cls][0]) == 0:
            version = classes_attributes_dict[cls][1]
            classes_attributes_dict.pop(cls, None)
            classes_attributes_dict[cls] = (get_class_fields(cls), version)
        if classes_attributes_dict[cls][1] == 'compact':
            tab = axes[row_index].table([[str(cls)]], loc='left')
            table_design(tab, colors[cls_index])
            axes[row_index].set_facecolor(colors[cls_index])
            axes[row_index].get_yaxis().set_visible(False)
            row_index += 1
        elif classes_attributes_dict[cls][1] == 'complete':
            for attribute in classes_attributes_dict[cls][0]:
                tab = axes[row_index].table([[str(cls + '_' + attribute)]], loc='left')
                table_design(tab, colors[cls_index])
                axes[row_index].set_facecolor(colors[cls_index])
                axes[row_index].get_yaxis().set_visible(False)
                row_index += 1

    return fig, axes


def table_design(table, color):
    """
    Set the design for the table column associated with each subplot.

    :param table: Table element in the plot.
    :param color: Color we want to associate to the table.

    :return:

    """
    table[0, 0].set_facecolor(color)
    table[0, 0].set_height(1)
    table[0, 0].set_width(0.25)


def get_class_fields(class_):
    """
    Get class attributes.

    :param class_: Classname as string.

    :return: List of the class attributes.

    """
    return list(eval(class_).__fields__)


def scatter_and_annotate_point(axes, index, x, y, color, size, marker, data_text, index_text, points, annotations):
    """
    Create scatter and annotation for a plot and put it in points and annotations list.

    :param axes: Axes from the considered plot.
    :param index: Index of the axe we want to scatter and annotate.
    :param x: Abscissa coordinate of the point to scatter and annotate.
    :param y: Ordinate coordinate of the point to scatter and annotate.
    :param color: Desired color for the scatter.
    :param size: Desired size for the scatter.
    :param marker: Desired marker for the scatter.
    :param data_text: Data to set as annotation.
    :param index_text: Index to set as annotation.
    :param points: List of scatter points.
    :param annotations: List of annotations.

    :return:

    """
    points.append(axes[index].scatter(x, y, c=color, s=size, marker=marker))
    ann_data = axes[index].annotate(data_text, xy=(x, y), bbox=dict(boxstyle="round4"))
    ann_index = axes[index].annotate(index_text, xy=(x, y), bbox=dict(boxstyle="round4"))
    annotations.append(ann_data)
    annotations.append(ann_index)
    ann_data.set_visible(False)
    ann_index.set_visible(False)


def get_x_y_marker(df_profile_not_na, i, xaxis):
    """
    Return x, y and marker for scatter profile point and annotations

    :param df_profile_not_na: Not null values from a profile dataframe.
    :param i: Index of the point we want to consider in the profile dataframe.
    :param xaxis: From which abscissa is displayed the data.

    :return: x, y, marker

    """
    x = df_profile_not_na.iloc[i][xaxis[-1]]
    y = 1
    if len(FIXED_COLUMNS) > 2 and not pd.isna(df_profile_not_na.iloc[i][FIXED_COLUMNS[2]]):
        marker = MARKERS[int(df_profile_not_na.iloc[i][FIXED_COLUMNS[2]] - 1)]
    else:
        marker = MARKERS[4]
    return x, y, marker


def display_profile(axes, df_profile, classes_attributes_dict, color='black', xaxis=[FIXED_COLUMNS[1]]):
    """
    Scatter points and their annotations in the profile figure.

    :param axes: Axes where we want to plot the profile.
    :param df_profile: Pandas dataframe of a MEDprofile.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param color: Desired color for scatter points.
    :param xaxis: From which abscissa is displayed the data.

    :return: points, annotations : List of points and list of annotations plotted in the MEDprofile plot.

    """
    # Initialize point and annotation lists
    points, annotations = [], []
    classes = list(classes_attributes_dict.keys())
    classes.sort()

    row_index = 0
    for cls_index, cls in enumerate(classes):
        if classes_attributes_dict[cls][1] == 'complete':
            for attribute in classes_attributes_dict[cls][0]:
                column_name = str(cls + '_' + attribute)
                df_profile_not_na = df_profile.dropna(subset=[column_name])
                for i in range(len(df_profile_not_na)):
                    if df_profile_not_na.iloc[i][xaxis[-1]] or df_profile_not_na.iloc[i][xaxis[-1]] == 0:
                        x, y, marker = get_x_y_marker(df_profile_not_na, i, xaxis)
                        scatter_and_annotate_point(axes, row_index, x, y, color, 10, marker,
                                                   df_profile_not_na.iloc[i][column_name], df_profile_not_na.index[0],
                                                   points, annotations)
                row_index += 1

        elif classes_attributes_dict[cls][1] == 'compact':
            columns_names = []
            for attribute in classes_attributes_dict[cls][0]:
                columns_names.append(str(cls + '_' + attribute))
            df_profile_not_na = df_profile.dropna(subset=columns_names, how='all')
            for i in range(len(df_profile_not_na)):
                annotation = ''
                nb_attributes_not_na = 0
                for attribute in classes_attributes_dict[cls][0]:
                    column_name = str(cls + '_' + attribute)
                    if df_profile_not_na.iloc[i][column_name]:
                        nb_attributes_not_na += 1
                        annotation += column_name + ' : ' + str(df_profile_not_na.iloc[i][column_name]) + '\n'
                annotation = annotation[:-1]
                if nb_attributes_not_na > 0:
                    x, y, marker = get_x_y_marker(df_profile_not_na, i, xaxis)
                    scatter_and_annotate_point(axes, row_index, x, y, color, 10 * nb_attributes_not_na, marker,
                                               annotation, df_profile_not_na.index[0],
                                               points, annotations)
            row_index += 1

    return points, annotations


def set_legend(fig, df_cohort):
    """
    Set legend in plot according to time_points present in the figure.

    :param fig: A MEDprofile plot.
    :param df_cohort: A MEDprofile pandas dataframe.

    :return: legend_points: list of according to the different time points in the figure.

    """
    # Get time points present in the figure
    time_points = set(df_cohort[FIXED_COLUMNS[2]])
    time_points = [t for t in time_points if pd.notna(t)]
    legend_points = []

    for time_point in time_points:
        time_point = int(time_point)
        legend_points.append(
            plt.scatter([], [], c='black', marker=MARKERS[time_point - 1], label=f'Time point {time_point}'))
    legend_points.append(fig.legend(loc='upper right'))
    return legend_points


def get_event_children_of_instance(event, instance):
    """
    Return children of the specified instance from an event.

    :param event: Matplotlib Event object.
    :param instance: Type of data we are looking for.

    :return: children: List of event's children of type instance.

    """
    children = []
    for child in event.inaxes.get_children():
        if isinstance(child, instance):
            if (instance == mpl.collections.PathCollection and len(
                    child.get_offsets()) > 0) or instance != mpl.collections.PathCollection:
                children.append(child)
    return children


def get_nearest_child(event, children):
    """
    Return the nearest child from the event.

    :param event: Matplotlib Event object.
    :param children: List of event's children to consider.

    :return: nearest_child : Nearest child from the event.

    """
    # Initialize the nearest child and min distance
    nearest_child = children[0]

    # Depending on type of the child, its x coordinate isn't the same attribute
    if isinstance(nearest_child, mpl.text.Annotation):
        x_data = children[0].xy[0]
    else:
        x_data = children[0].get_offsets()[0][0]

    # If x coord is date or timestamp, we have to transform it to calculate distances
    if isinstance(x_data, pd._libs.tslibs.timestamps.Timestamp) or isinstance(x_data, datetime.date):
        min_distance = (event.xdata - mpl.dates.date2num(x_data)) ** 2
    else:
        min_distance = (event.xdata - x_data) ** 2

    # Same as before, but iterate over all the children
    for child in children[1:]:
        if isinstance(child, mpl.text.Annotation):
            x_data = child.xy[0]
        else:
            x_data = child.get_offsets()[0][0]
        if isinstance(x_data, pd._libs.tslibs.timestamps.Timestamp) or isinstance(x_data, datetime.date):
            distance = (event.xdata - mpl.dates.date2num(x_data)) ** 2
        else:
            distance = (event.xdata - x_data) ** 2

        # Get the min distance corresponding to the nearest child
        if distance < min_distance:
            nearest_child = child
            min_distance = distance
    return nearest_child


def get_class(event):
    """
    Get class of the axis where the event occurs.

    :param event: Matplotlib Event object.

    :return: Matching class or None.

    """
    for child in event.inaxes.get_children():
        if isinstance(child, mpl.table.Table):
            return child._cells[(0, 0)].get_text().get_text().split('_')[0]
    return None


def get_axes_index_of_class(axes, class_):
    """
    Return a list of the axes indexes related to the specified class.

    :param axes: Axes from a MEDprofile plot.
    :param class_: Classname string of the class to consider.

    :return: index_list: List of the axes indexes related to the specified class.

    """
    index_list = []
    for axis_index in range(len(axes)):
        for child in axes[axis_index].get_children():
            if isinstance(child, mpl.table.Table):
                axis_class = child._cells[(0, 0)].get_text().get_text().split('_')[0]
                if class_ == axis_class:
                    index_list.append(axis_index)
    return index_list


def remove_from_plot(data):
    """
    Remove data from plot.

    :param data: List of data present in a plot.

    :return:

    """
    for element in data:
        element.remove()


def display_annotations(event):
    """
    Display or hide the nearest annotation.

    :param event: Matplotlib Event object.

    :return:

    """
    children = get_event_children_of_instance(event, mpl.text.Annotation)
    if len(children) > 0:
        child = get_nearest_child(event, children)
        # Case annotation is hidden
        if not child.get_visible():
            child.set_visible(True)
        # Case annotation is visible
        else:
            child.set_visible(False)


def set_time_relative_to_class_in_profile(df_profile, cls):
    """
    Set relative time at cls in df_profile.

    :param df_profile: MEDprofile pandas dataframe.
    :param cls: Classname string of the class we consider.

    :return:

    """
    df_profile[FIXED_COLUMNS[1]] = pd.to_datetime(df_profile[FIXED_COLUMNS[1]], format=DATE_FORMAT)

    # Get column_names relative to class
    column_names = []
    for attribute in eval(cls).__fields__:
        column_names.append(str(cls + '_' + attribute))

    # Case there is no value for the selected class
    if len(df_profile.dropna(subset=column_names, how='all')[FIXED_COLUMNS[1]]) == 0:
        return
    # Set relative date to the first date
    else:
        if len(df_profile.dropna(subset=column_names, how='all')[FIXED_COLUMNS[1]]) > 1:
            first_date = min(df_profile.dropna(subset=column_names, how='all')[FIXED_COLUMNS[1]])
        else:
            first_date = df_profile.dropna(subset=column_names, how='all')[FIXED_COLUMNS[1]]

    df_profile['Days_from_relative_date'] = df_profile[FIXED_COLUMNS[1]] - first_date
    df_profile['Days_from_relative_date'] = pd.to_numeric(df_profile['Days_from_relative_date'].dt.days,
                                                          downcast='integer')


def set_relative_time_in_profile_plot(event, axes, df_profile, classes_attributes_dict, xaxis, dict_points,
                                      dict_annotations):
    """
    Set relative time considering the class associated to axis where the event happens.

    :param event: Matplotlib Event object.
    :param axes: Axes from a MEDprofile plot.
    :param df_profile: Pandas dataframe of a MEDprofile.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param xaxis: From which abscissa is displayed the data.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.

    :return:

    """
    class_ = get_class(event)

    patient_id = list(dict_points.keys())[0]
    remove_from_plot(dict_points[patient_id])
    remove_from_plot(dict_annotations[patient_id])
    dict_points.pop(patient_id, None)
    dict_annotations.pop(patient_id, None)

    set_time_relative_to_class_in_profile(df_profile, class_)

    xaxis.append('Days_from_relative_date')
    xaxis.pop(0)
    points, annotations = display_profile(axes, df_profile, classes_attributes_dict, xaxis=xaxis)
    dict_points[patient_id] = points
    dict_annotations[patient_id] = annotations
    axes[0].xaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
    plt.xlabel('Days from relative time', fontsize=12)


def set_absolute_time_in_profile_plot(axes, df_profile, classes_attributes_dict, xaxis, dict_points, dict_annotations):
    """
    Display profile by absolute time in plot.

    :param axes: Axes from a MEDprofile plot.
    :param df_profile: Pandas dataframe of a MEDprofile.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param xaxis: From which abscissa is displayed the data.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.

    :return:

    """
    patient_id = list(dict_points.keys())[0]
    remove_from_plot(dict_points[patient_id])
    remove_from_plot(dict_annotations[patient_id])
    dict_points.pop(patient_id, None)
    dict_annotations.pop(patient_id, None)
    xaxis.append(FIXED_COLUMNS[1])
    xaxis.pop(0)
    points, annotations = display_profile(axes, df_profile, classes_attributes_dict, xaxis=xaxis)
    dict_points[patient_id] = points
    dict_annotations[patient_id] = annotations
    axes[0].xaxis.set_major_formatter(mpl.dates.DateFormatter(DATE_FORMAT))
    plt.xlabel('Date', fontsize=12)


def is_time_relative_to_selected_class(event, xaxis, df):
    """
    Return True if the event occurs on the axe of the relative class for time.

    :param event: Matplotlib Event object.
    :param xaxis: From which abscissa is displayed the data.
    :param df: Profile or cohort dataframe.

    :return: True if time is relative to the event class, False otherwise.

    """
    if xaxis[-1] == FIXED_COLUMNS[1] or 'Days_from_relative_date' not in df.columns:
        return False

    cls = get_class(event)
    class_fields = get_class_fields(cls)
    column_names = []
    for field in class_fields:
        column_names.append(str(cls + '_' + field))

    # Check if all selected class points for all patients are at 0
    min_point_patient = []
    for patient_id in set(df.index):
        if len(df.loc[patient_id].dropna(subset=column_names, how='all')) > 0:
            min_point_patient.append(
                min(df.loc[patient_id].dropna(subset=column_names, how='all')['Days_from_relative_date']))

    return all(x == 0 for x in min_point_patient)


def center_data_in_profile_plot(dict_points):
    """
    Center plot on current data.

    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.

    :return:

    """
    list_x = []
    patient_id = list(dict_points.keys())[0]
    for point in dict_points[patient_id]:
        list_x.append(point.get_offsets().data[0][0])
    distance_to_edge = (max(list_x) - min(list_x)) / len(list_x)
    plt.xlim(min(list_x) - distance_to_edge, max(list_x) + distance_to_edge)


def r_pressed_in_profile(event, axes, df_profile, classes_attributes_dict, xaxis, dict_points, dict_annotations):
    """
    Called when button r is pressed on a profile figure. Set or remove the relative time.

    :param event: Matplotlib Event object.
    :param axes: Axes from a MEDprofile plot.
    :param df_profile: Pandas dataframe of a MEDprofile.
    :param classes_attributes_dict: Dict associating classes to the attributes we want to display and format (one row
           for the class or one row by attributes to display in the class). Keys are class names and values are tuples
           (list of attributes, format), with format equals to 'compact' or 'complete'.
    :param xaxis: From which abscissa is displayed the data.
    :param dict_points: Dict associating MEDprofile PatientID to the list of corresponding points in Axes.
    :param dict_annotations: Dict associating MEDprofile PatientID to the list of corresponding annotations in Axes.

    :return:

    """
    # If time is relative we set absolute time
    if is_time_relative_to_selected_class(event, xaxis, df_profile):
        set_absolute_time_in_profile_plot(axes, df_profile, classes_attributes_dict, xaxis, dict_points,
                                          dict_annotations)
    # If time is absolute we set relative time
    else:
        set_relative_time_in_profile_plot(event, axes, df_profile, classes_attributes_dict, xaxis, dict_points,
                                          dict_annotations)
