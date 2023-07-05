import datetime
from pydantic import validator
from MEDclasses import *
from MEDclasses.MEDbaseObject import MEDbaseObject
from typing import Optional
from src.back.constant import DATE_FORMAT


class MEDtab(MEDbaseObject):
    Date: Optional[datetime.datetime]
    Time_point: Optional[float]
    demographic: Optional[demographic]
    chartevent: Optional[chartevent]
    labevent: Optional[labevent]
    vd: Optional[vd]
    vp: Optional[vp]
    vmd: Optional[vmd]
    vmp: Optional[vmp]
    necg: Optional[necg]
    nech: Optional[nech]
    nrad: Optional[nrad]
    procedureevent: Optional[procedureevent]

    @validator("Date", pre=True)
    @classmethod
    def parse_date(cls, value):
        value = str(value)
        if value and value != 'nan':
            return datetime.datetime.strptime(value, DATE_FORMAT).date()




