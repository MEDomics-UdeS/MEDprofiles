"""

Definitions of constants depending on the master table used.

"""

# MENINGIOMA DATA

# INDEX_TYPE_ROW = 0
# INDEX_ATTRIBUTE_ROW = 1
# FIXED_COLUMNS = ['PatientID', 'Date', 'Time_point']
# FIXED_COLUMNS_TYPES = ['str', 'datetime.date', 'float']
# DATE_FORMAT = '%Y-%m-%d'
# MARKERS = ['o', 'v', 's', '*', 'D']


# MIMIC DATA

INDEX_TYPE_ROW = 1
INDEX_ATTRIBUTE_ROW = 0
FIXED_COLUMNS = ['PatientID', 'Date', 'Time_point']
FIXED_COLUMNS_TYPES = ['str', 'datetime.datetime', 'float']
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
MARKERS = ['o', 'v', 's', '*', 'D']
