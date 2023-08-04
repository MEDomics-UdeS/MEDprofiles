import datetime
from pydantic import validator
from ..MEDclasses import *
from typing import Optional
from MEDprofiles.src.back.constant import DATE_FORMAT


class MEDtab(MEDbaseObject):
    pass

    @validator("Date", pre=True, check_fields=False)
    @classmethod
    def parse_date(cls, value):
        value = str(value)
        if value and value != 'nan':
            return datetime.datetime.strptime(value, DATE_FORMAT).date()




