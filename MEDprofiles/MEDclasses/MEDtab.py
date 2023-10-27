import datetime
from pydantic import validator
from .MEDbaseObject import MEDbaseObject
from typing import Optional


class MEDtab(MEDbaseObject):
    pass

    @validator("Date", pre=True, check_fields=False)
    @classmethod
    def parse_date(cls, value):
        value = str(value)
        if value and value != 'nan':
            return datetime.datetime.strptime(value, __import__('MEDprofiles').src.back.constant.DATE_FORMAT).date()




