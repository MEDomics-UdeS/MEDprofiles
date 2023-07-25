"""

Take a master table as entry and create dynamically classes based on the table attributes using pydantic package.

"""
import os
import pandas as pd

from ..back import constant


def get_classes_from_df(df):
    """
    Create a classes dict from a pandas dataframe. DataFrame columns names must be like ClassName_ClassAttribute and
    must contain a row for column types.

    :param df: The pandas dataframe.

    :return: classes_dict: Dict where keys are classes and values are lists of tuples(class_attribute,
             class_attribute_type, True).

    """
    classes_dict = {}
    for column in df.columns:
        pos = column.find('_')
        if pos != -1:
            class_name = column[0:pos]
            class_attribute = column[pos + 1:]
            class_attribute_type = df[column][constant.INDEX_TYPE_ROW]
            if class_attribute_type == 'num':
                class_attribute_type = 'float'
            if class_name not in classes_dict:
                classes_dict[class_name] = []
            classes_dict[class_name].append((class_attribute, class_attribute_type, True))
    return classes_dict


def create_class_file(path, class_name, attribute_list, base_class, directory_name):
    """
    Define a class in a new file in a specific path.

    :param: path: Path where place the class definition.
    :param: class_name: Name of the class we define.
    :param: attribute_list: Attribute list of the class we define, elements of the list may be tuples (attribute, type,
            boolean) if boolean is true, the attribute is optional.

    :return:

    """
    tab = "    "
    class_path = os.path.join(path, class_name + ".py")
    with open(class_path, "w") as file:
        file.write("from typing import Optional\n")
        file.write("from " + directory_name + ".MEDbaseObject import MEDbaseObject\n\n\n")
        file.write("class " + class_name + "(" + base_class + "):\n")
        for attribute in attribute_list:
            if attribute[2]:
                file.write(tab + str(attribute[0]) + ": Optional[" + str(attribute[1]) + "]\n")
            else:
                file.write(tab + str(attribute[0]) + ": " + str(attribute[1]) + "\n")
        file.write("\n\n")
    file.close()


def add_attributes_to_class(path, class_name, attribute_list, types_list, base_class):
    """
    Add attributes from attribute_list to class file with class defined as class_name(base_class).

    :param path: Directory of the class file.
    :param class_name: Name of the considered class.
    :param attribute_list: Attributes to add.
    :param types_list: Types of the attributes to add.
    :param base_class: Class from which the class we create inherit.

    :return:

    """
    tab = "    "
    class_path = os.path.join(path, class_name + ".py")
    with open(class_path, "r") as file:
        data = file.readlines()
    file.close()
    new_data = []
    for line in data:
        if "pass" not in line:
            new_data.append(line)
        # Check if the attributes are not already in the class definition and add them at the right place
        if line == "class " + class_name + '(' + base_class + '):\n' and tab + attribute_list[0] + ": Optional[" + \
                attribute_list[0] + "]\n" not in data:
            for i in range(len(attribute_list)):
                new_data.append(tab + attribute_list[i] + ": Optional[" + types_list[i] + "]\n")
    with open(class_path, "w") as file:
        file.writelines(new_data)
    file.close()


def main(arg):
    """
    Main function for class creation.

    :param arg: Path to the master table from which we create the classes.

    :return:

    """
    # Get value from the master table
    df = pd.read_csv(arg, header=None, on_bad_lines='skip', low_memory=False)
    df.columns = df.iloc[constant.INDEX_ATTRIBUTE_ROW]

    # Group attributes by classes
    classes_attributes_dict = get_classes_from_df(df.drop(constant.FIXED_COLUMNS, axis=1))

    # Create directory MEDclasses for classes
    directory_name = 'MEDclasses'
    directory_path = '../../MEDclasses'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Create classes
    for class_ in classes_attributes_dict:
        create_class_file(directory_path, class_, classes_attributes_dict[class_], "MEDbaseObject", directory_name)

    # Set dynamic attributes in MEDtab class
    add_attributes_to_class(directory_path, "MEDtab", list(classes_attributes_dict.keys()),
                            list(classes_attributes_dict.keys()), "MEDbaseObject")

    # Set constant attributes in MEDtab class
    add_attributes_to_class(directory_path, "MEDtab", constant.FIXED_COLUMNS[1:], constant.FIXED_COLUMNS_TYPES[1:], "MEDbaseObject")

    # Create __init__ file
    init_path = os.path.join(directory_path, "__init__.py")
    with open(init_path, "w") as file:
        for class_ in list(classes_attributes_dict.keys()) + ["MEDtab", "MEDprofile", "MEDcohort", "MEDbaseObject"]:
            file.write("from " + directory_name + "." + class_ + " import " + class_ + "\n")
    file.close()


if __name__ == '__main__':
    main('../../data/mimic/csv/master_table.csv')
    #main('../../data/meningioma/csv/master_table.csv')
