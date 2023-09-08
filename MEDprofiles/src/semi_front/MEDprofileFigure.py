import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from MEDprofiles.src.back.constant import FIXED_COLUMNS
from MEDprofiles.src.semi_front.utils.MEDprofiles_utils import center_data_in_profile_plot, display_annotations, \
    display_profile, r_pressed_in_profile, set_plot


def button_pressed(event):
    """
    Show or hide annotations if the event occurs.

    :param event: A Matplolib event.

    :return:

    """
    if event.button == mpl.backend_bases.MouseButton.LEFT or event.button == mpl.backend_bases.MouseButton.RIGHT:
        display_annotations(event)
    plt.gcf().canvas.draw_idle()


class MEDprofileFigure:
    """
    Class representing an interactive figure for a MEDprofile.
    """
    def __init__(self, classes_attributes_dict, patient_id, profile_df, plot_width=10, subplot_height=1,
                 xaxis=[FIXED_COLUMNS[1]]):
        self.annotations = []
        self.classes_attributes_dict = classes_attributes_dict
        self.colors = mpl.colormaps['Blues'](np.linspace(0, 1, len(classes_attributes_dict.keys()) + 1))
        self.dict_annotations = {}
        self.dict_points = {}
        self.patient_id = patient_id
        self.plot_width = plot_width
        self.points = []
        self.profile_df = profile_df
        self.subplot_height = subplot_height
        self.xaxis = xaxis

        self.fig, self.axes = set_plot(self.subplot_height, self.plot_width, self.classes_attributes_dict, self.colors)
        self.set_figure()

    def set_figure(self):
        """
        Prepare the interactive figure.
        """
        self.fig.canvas.mpl_connect('button_press_event', button_pressed)
        self.fig.canvas.mpl_connect('key_press_event', self.key_pressed)
        self.points, self.annotations = display_profile(self.axes, self.profile_df, self.classes_attributes_dict)
        self.dict_points[self.patient_id] = self.points
        self.dict_annotations[self.patient_id] = self.annotations
        self.fig.suptitle(f'MEDprofile of patient {self.patient_id}', fontsize=16)
        plt.xlabel('Date', fontsize=12)

    def key_pressed(self, event):
        """
        Called when a key pressed event occurs.

        :param event:
        :return:

        """
        # Set relative time at the class matching the axis in which the event occurs
        if event.key == 'r':
            r_pressed_in_profile(event, self.axes, self.profile_df, self.classes_attributes_dict, self.xaxis,
                                 self.dict_points, self.dict_annotations)
        center_data_in_profile_plot(self.dict_points)
        self.fig.canvas.draw()
