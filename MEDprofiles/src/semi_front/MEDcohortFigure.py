import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from MEDprofiles.src.back.constant import FIXED_COLUMNS
from MEDprofiles.src.semi_front.BinFigure import BinFigure
from MEDprofiles.src.semi_front.MEDprofileFigure import MEDprofileFigure
from MEDprofiles.src.semi_front.utils.MEDcohort_utils import delete_pressed, display_attributes_values, display_cohort,\
    display_patient_id_and_data, r_pressed, t_pressed
from MEDprofiles.src.semi_front.utils.MEDprofiles_utils import set_plot


class MEDcohortFigure:

    def __init__(self, classes_attributes_dict, cohort_df, plot_width=10, subplot_height=1, xaxis=[FIXED_COLUMNS[1]]):
        self.classes_attributes_dict = classes_attributes_dict
        self.cohort_df = cohort_df
        self.colors = mpl.colormaps['Blues'](np.linspace(0, 1, len(classes_attributes_dict.keys()) + 1))
        self.dict_annotations = {}
        self.dict_class_time_points = {}
        self.dict_points = {}
        self.dict_profile_figures = {}
        self.dict_selected_annotations = {}
        self.dict_selected_points = {}
        self.legend_points = []
        self.plot_width = plot_width
        self.subplot_height = subplot_height
        self.title = ""
        self.xaxis = xaxis

        self.fig, self.axes = set_plot(self.subplot_height, self.plot_width, self.classes_attributes_dict, self.colors)
        self.set_figure()

    def set_figure(self):
        """
        Prepare the interactive figure.
        """
        self.fig.canvas.mpl_connect('button_press_event', self.button_pressed)
        self.fig.canvas.mpl_connect('key_press_event', self.key_pressed)
        # fig.canvas.mpl_connect('close_event', on_close)
        plt.xlabel("Date", fontsize=12)
        display_cohort(self.axes, self.cohort_df, self.classes_attributes_dict, self.dict_points, self.dict_annotations,
                       self.xaxis)
        self.title = self.fig.suptitle(f'MEDcohort composed by {len(set(self.cohort_df.index))} patients', fontsize=16)

    def button_pressed(self, event):
        """
        Called when a button pressed event occurs.

        :param event:
        :return:

        """
        # If the button pressed is the left MouseButton we display the data of
        # the nearest point in the axis
        if event.button == mpl.backend_bases.MouseButton.LEFT:
            display_attributes_values(event, self.cohort_df)

        # If the button pressed is the right MouseButton we highlight the patient
        # points in all the plot (for the nearest patient)
        elif event.button == mpl.backend_bases.MouseButton.RIGHT:
            display_patient_id_and_data(event, self.axes, self.cohort_df, self.classes_attributes_dict,
                                        self.dict_points, self.dict_annotations, self.dict_selected_points,
                                        self.dict_selected_annotations, self.xaxis)
        self.fig.canvas.draw()

    def key_pressed(self, event):
        """
        Called when a key pressed event occurs.

        :param event:
        :return:

        """
        # Delete selected patients while delete key is pressed
        if event.key == 'delete':
            delete_pressed(self.dict_points, self.dict_selected_points, self.dict_selected_annotations, self.title)
        # Set relative time at the class matching the axis in which the event occurs
        elif event.key == 'r':
            r_pressed(event, self.axes, self.cohort_df, self.classes_attributes_dict, self.dict_points,
                      self.dict_annotations, self.dict_selected_points, self.dict_selected_annotations, self.xaxis)
        # Set time points
        elif event.key == 't':
            t_pressed(event, self.axes, self.cohort_df, self.classes_attributes_dict, self.dict_points,
                      self.dict_annotations, self.dict_selected_points, self.dict_selected_annotations, self.xaxis,
                      self.dict_class_time_points, self.legend_points, self.fig)
        # Open selected profiles
        elif event.key == 'p':
            for patient_id in self.dict_selected_points.keys():
                self.dict_profile_figures[patient_id] = MEDprofileFigure(self.classes_attributes_dict, patient_id,
                                                                         self.cohort_df.loc[[patient_id]],
                                                                         self.plot_width, self.subplot_height,
                                                                         self.xaxis)
        # Open bin figure
        elif event.key == 'y' or event.key == 'm':
            if event.key == 'y':
                frequency = 'year'
            else:
                frequency = 'month'
            BinFigure(self.classes_attributes_dict, self.cohort_df, frequency, self.plot_width, self.subplot_height)
        plt.gcf().canvas.draw_idle()
