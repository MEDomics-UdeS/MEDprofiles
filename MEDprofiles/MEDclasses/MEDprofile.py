from typing import List
from .MEDtab import *
from typing import Optional


class MEDprofile(MEDbaseObject):
    """
    MEDprofile represent a patient in the master table.

    :param PatientID:
    :param list_MEDtab:

    """
    PatientID: str
    list_MEDtab: Optional[List[MEDtab]] = None

    def filter_med_tab_from_profile(self, attribute_filter_dict, all_necessary_in_attribute=True, all_necessary=True):
        """
        Return a profile where elements from list_MEDTab match attribute_filter_dict.

        :param attribute_filter_dict:
        :param all_necessary_in_attribute:
        :param all_necessary:
        :return: MEDProfile: filtered MEDProfile

        """
        filtered_med_tab_list = []
        for med_tab in self.list_MEDtab:
            if med_tab.are_attributes_in_filter(attribute_filter_dict, all_necessary_in_attribute, all_necessary):
                filtered_med_tab_list.append(med_tab)
        return MEDprofile(PatientID=self.PatientID, list_MEDtab=filtered_med_tab_list)

    def are_med_tab_in_filter(self, attribute_filter_dict, all_necessary_in_attribute=True, all_necessary=True,
                              all_med_tab_necessary=True):
        """
        Return True if elements from list_MEDTab match the attribute_filter_dict. If all_med_tab_necessary is True, all
        the MEDTab must match the filters, if all_med_tab_necessary is False the function returns True if at least one
        MEDTab match the filters.

        :param attribute_filter_dict:
        :param all_necessary_in_attribute:
        :param all_necessary:
        :param all_med_tab_necessary:
        :return: True or False

        """
        nb_matching_med_tab = 0
        for med_tab in self.list_MEDtab:
            if med_tab.are_attributes_in_filter(attribute_filter_dict, all_necessary_in_attribute, all_necessary):
                if not all_med_tab_necessary:
                    return True
                nb_matching_med_tab += 1
        if len(self.list_MEDtab) == nb_matching_med_tab:
            return True
        return False
