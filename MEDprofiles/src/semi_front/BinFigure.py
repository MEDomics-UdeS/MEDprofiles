import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from MEDprofiles.src.semi_front.utils.MEDcohort_utils import scatter_bin_points, set_in_bin
from MEDprofiles.src.semi_front.utils.MEDprofiles_utils import display_annotations, set_plot


def set_classes_dict_in_compact_format(classes_attributes_dict):
    compact_dict = {}
    for cls in classes_attributes_dict:
        compact_dict[cls] = ([], 'compact')
    return compact_dict


def button_pressed(event):
    if event.button == mpl.backend_bases.MouseButton.LEFT or event.button == mpl.backend_bases.MouseButton.RIGHT:
        display_annotations(event)
        plt.gcf().canvas.draw_idle()


class BinFigure:

    def __init__(self, classes_attributes_dict, cohort_df, frequency, plot_width=10, subplot_height=1):
        self.classes_attributes_dict = set_classes_dict_in_compact_format(classes_attributes_dict)
        self.cohort_df = cohort_df
        self.colors = mpl.colormaps['Blues'](np.linspace(0, 1, len(self.classes_attributes_dict.keys()) + 1))
        self.dict_annotations = {}
        self.dict_points = {}
        self.frequency = frequency
        self.plot_width = plot_width
        self.subplot_height = subplot_height
        self.title = ""

        self.data_dict = set_in_bin(self.cohort_df, self.classes_attributes_dict, self.frequency)
        self.fig, self.axes = set_plot(self.subplot_height, self.plot_width, self.classes_attributes_dict, self.colors)
        self.set_figure()

    def set_figure(self):
        """
        Prepare the interactive figure.
        """
        self.fig.canvas.mpl_connect('button_press_event', button_pressed)
        plt.xlabel("Date", fontsize=12)
        scatter_bin_points(self.axes, self.classes_attributes_dict, self.data_dict, self.dict_points,
                           self.dict_annotations)
        self.title = self.fig.suptitle(
            f'MEDcohort in bin ({self.frequency}) composed by {len(set(self.cohort_df.index))} patients', fontsize=16)
