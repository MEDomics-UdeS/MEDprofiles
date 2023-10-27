from pydantic import BaseModel
from .MEDprofile import *
import pandas as pd


class MEDcohort(BaseModel):
    """
    MEDcohort represent a set of patients profiles.

    :param list_MEDprofile:

    """
    list_MEDprofile: List[MEDprofile]

    def filter_med_profile_from_cohort(self, attribute_filter_dict, all_necessary_in_attribute=True, all_necessary=True,
                                       all_med_tab_necessary=True, filter_med_tab=True):
        """
        Filter list_MEDProfile according to attribute_filter_dict.

        :param attribute_filter_dict:
        :param all_necessary_in_attribute:
        :param all_necessary:
        :param all_med_tab_necessary:
        :param filter_med_tab:
        :return: MEDCohort with matching list_MEDProfile

        """
        filtered_med_profile_list = []
        for med_profile in self.list_MEDprofile:
            if med_profile.are_med_tab_in_filter(attribute_filter_dict, all_necessary_in_attribute, all_necessary,
                                                 all_med_tab_necessary):
                filtered_med_profile_list.append(med_profile)
        if not all_med_tab_necessary and filter_med_tab:
            temp = []
            for profile in filtered_med_profile_list:
                temp.append(profile.filter_med_tab_from_profile(attribute_filter_dict, all_necessary_in_attribute,
                                                                all_necessary))
            filtered_med_profile_list = temp
        return MEDcohort(list_MEDprofile=filtered_med_profile_list)

    def profile_list_to_df(self, attribute_list=None, by_sub_attributes=True):
        """
        Return list_MEDProfile values as a dataframe where columns are defined by attribute list.

        :param attribute_list: attributes to consider in the dataframe
        :param by_sub_attributes: if True, consider sub-attributes from attributes as columns
        :return: df: pandas dataframe

        """
        # If attribute list isn't set, we consider all the attributes
        if not attribute_list:
            attribute_list = list(MEDtab.__fields__.keys())
            for element in __import__('MEDprofiles').src.back.constant.FIXED_COLUMNS[1:]:
                attribute_list.remove(element)

        # If by_sub_attributes is True, all sub-attributes are considered as columns
        if by_sub_attributes:
            temp = []
            for attribute in attribute_list:
                for sub_attribute in eval(attribute).__fields__.keys():
                    temp.append(attribute + '_' + sub_attribute)
            attribute_list = temp

        # Get data
        rows = []
        for profile in self.list_MEDprofile:
            for tab in profile.list_MEDtab:
                row = [profile.PatientID]
                for element in __import__('MEDprofiles').src.back.constant.FIXED_COLUMNS[1:]:
                    row.append(tab.__dict__[element])
                for attribute in attribute_list:
                    if by_sub_attributes:
                        row.append(
                            tab.__dict__[attribute[:attribute.find('_')]].__dict__[attribute[attribute.find('_') + 1:]])
                    else:
                        row.append(tab.__dict__[attribute])
                rows.append(row)

        # Set fixed columns at the beginning of attribute list
        attribute_list = __import__('MEDprofiles').src.back.constant.FIXED_COLUMNS + attribute_list

        # Create the pandas dataframe
        df = pd.DataFrame(rows, columns=attribute_list).set_index(attribute_list[0])
        return df

    def summarize_data(self):
        """
        Display information about cohort, Tab attributes, number of columns/rows, Nan percentage, means and modes.

        :return:

        """
        # Get complete df for cohort
        df = self.profile_list_to_df()

        # Display general information
        print('Number of classes : ', len(MEDtab.__fields__))
        print('Number of attributes : ', len(df.columns))
        print('Number of profiles : ', len(self.list_MEDprofile))
        print('Number of row (time series data) : ', len(df))
        print('Mean of row (time series data) number per profile : ', round(len(df) / len(self.list_MEDprofile), 2),
              '\n')

        # Display information by attribute
        for attribute in MEDtab.__fields__:
            print(attribute, MEDtab.__fields__[attribute].type_)
            if attribute not in __import__('MEDprofiles').src.back.constant.FIXED_COLUMNS:
                print('Number of attributes in class : ', len(eval(attribute).__fields__))
                for sub_attribute in eval(attribute).__fields__:
                    print('\t', sub_attribute, eval(attribute).__fields__[sub_attribute].type_)
                    print('\t\t%Nan : ', round(
                        df[attribute + '_' + sub_attribute].isnull().sum() / len(df[attribute + '_' + sub_attribute]),
                        2))
                    if eval(attribute).__fields__[sub_attribute].type_ == float:
                        print('\t\tMean : ', round(df[attribute + '_' + sub_attribute].mean(), 2))
                    else:
                        print('\t\tMode : ', df[attribute + '_' + sub_attribute].mode()[0])
            else:
                print('\t%Nan : ', round(df[attribute].isnull().sum() / len(df[attribute]), 2))
            print('\n')
