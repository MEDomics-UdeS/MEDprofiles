from pydantic import BaseModel


class MEDbaseObject(BaseModel):
    """
    MEDbaseObject is the base of other classes, containing filter functions.
    """

    def is_attribute_in_filter(self, attribute, filter):
        """
        Function that return True if the object's attribute match the filter and False if not. Filter may be a tuple (in
        this case consider an interval), a list (return True if the object attribute is contained in the list) or a
        simple value.

        :param attribute:
        :param filter:
        :return: True or False

        """
        if not self.__dict__[attribute]:
            return False
        # If filter is a tuple we search an interval
        if type(filter) == tuple:
            if filter[0] and filter[1]:
                return filter[0] <= self.__dict__[attribute] <= filter[1]
            if filter[0]:
                return filter[0] <= self.__dict__[attribute]
            if filter[1]:
                return self.__dict__[attribute] <= filter[1]
            return True
        # If filter is a list we search if the list contain the attribute value
        if type(filter) == list:
            return self.__dict__[attribute] in filter
        # Else we just compare values
        return self.__dict__[attribute] == filter

    def are_attributes_in_filter(self, attribute_filter_dict, all_necessary_in_attribute=True, all_necessary=True):
        """
        Function that take a dict as entry, associating object attributes and expected values. If all_necessary is True
        the function return True if all the attribute dict elements match their filters, False in the other case. If
        all_necessary is set to False, the function return True if at least one attribute match the filter. The same
        principle is applicated to class objects with the parameter all_necessary_in_attribute.

        :param attribute_filter_dict:
        :param all_necessary_in_attribute:
        :param all_necessary:
        :return: True or False

        """
        nb_matching_attributes = 0
        for attribute in attribute_filter_dict:
            # If attribute is class instance
            if type(attribute_filter_dict[attribute]) == dict:
                if self.__dict__[attribute].are_attributes_in_filter(attribute_filter_dict[attribute],
                                                                     all_necessary=all_necessary_in_attribute):
                    if not all_necessary:
                        return True
                    nb_matching_attributes += 1
            # If the attribute is not class instance
            else:
                if self.is_attribute_in_filter(attribute, attribute_filter_dict[attribute]):
                    if not all_necessary:
                        return True
                    nb_matching_attributes += 1
        # Case all_necessary is set to True
        if nb_matching_attributes == len(attribute_filter_dict):
            return True
        return False
