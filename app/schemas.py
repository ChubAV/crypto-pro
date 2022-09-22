from typing import Optional, Union, List
from datetime import datetime

from pydantic import BaseModel, validator, Field

def normalize_date(v: Union[str, datetime]) -> datetime:
    if isinstance(v, datetime):
        return v
    return datetime.strptime(v, '%d.%m.%Y %H:%M:%S')



class CertificateSchema(BaseModel):
    subject_name: str
    issuer_name: str
    thumbprint: str
    serial_number: str
    valid_from_date: datetime
    valid_to_date: datetime
    certificate: Optional[str] = None
    
    _valid_from_date = validator('valid_from_date', pre=True, allow_reuse=True)(normalize_date)
    _valid_to_date = validator('valid_to_date', pre=True, allow_reuse=True)(normalize_date)

class ListCertificatesSchema(BaseModel):
    count:  int = 0
    certificates: List[CertificateSchema] = []

class ErrorSchema(BaseModel):
    code: str = Field(title="Код ошибки")
    description: str = Field(title='Описание ошибки')

class SingSchema(BaseModel):
    singer: CertificateSchema
    date_sign: datetime

    _date_sign = validator('date_sign', pre=True, allow_reuse=True)(normalize_date)

class AboutSchema(BaseModel):
    csp_version: str = Field(title='Версия Крипто-Про')
    sdk_version: str = Field(title='Версия SDK Крипто-Про')
    pycades_version: str = Field(title='Версия pycades')
    python_version: str = Field(title='Версия Python')
    platform_version: str = Field(title='Версия ОС')

class ResponseSchema(BaseModel):
    result: bool = Field(default=False, title='Результат')
    details: Optional[Union[CertificateSchema, SingSchema, AboutSchema, ListCertificatesSchema]] = Field(default=None, title='Детали')
    errors: Optional[ErrorSchema] = Field(default=None, title='Ошибки')



