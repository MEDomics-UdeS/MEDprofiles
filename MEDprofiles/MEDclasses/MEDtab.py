import datetime
from pydantic import validator
from MEDclasses import *
from MEDclasses.MEDbaseObject import MEDbaseObject
from typing import Optional
from src.back.constant import DATE_FORMAT


class MEDtab(MEDbaseObject):
    pass

    @validator("Date", pre=True)
    @classmethod
    def parse_date(cls, value):
        value = str(value)
        if value and value != 'nan':
            return datetime.datetime.strptime(value, DATE_FORMAT).date()




