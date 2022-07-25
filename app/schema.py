from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr


class AddressBase(BaseModel):
    city: Optional[str]
    street: Optional[str]
    number: Optional[str]
    zip: Optional[str]


class AddressCreate(AddressBase):
    pass


class Address(AddressBase):
    id: UUID

    class Config:
        orm_mode = True


class CompanyCheck(BaseModel):
    name: Optional[str]
    id_number: Optional[str]


class PersonCheck(BaseModel):
    id: str
    companies: Optional[List[CompanyCheck]] = []


class PersonBase(BaseModel):
    email: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    country: Optional[str]
    id_number: Optional[str]
    document_type: Optional[str]
    document_number: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    requested_at: Optional[datetime]
    verified_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True


class Person(PersonBase):
    id: UUID
    company_id: Optional[UUID]
    addresses: List[Address] = []

    class Config:
        orm_mode = True


class CompanyBase(BaseModel):
    id_number: str
    dic: Optional[str]
    name: Optional[str]
    registry: Optional[str]
    status: Optional[str]
    address: Optional[AddressCreate]


class PersonCreate(PersonBase):
    address: Optional[AddressCreate]
    document_front: Optional[str]
    document_back: Optional[str]
    document_verification_photo: Optional[str]
    company: Optional[UUID]


class PersonVerify(BaseModel):
    id: UUID
    address: Optional[AddressCreate]
    name: Optional[str]
    surname: Optional[str]
    country: Optional[str]
    id_number: Optional[str]
    document_type: Optional[str]
    document_number: Optional[str]
    document_front: Optional[str]
    document_back: Optional[str]
    document_verification_photo: Optional[str]


class PersonUpdate(BaseModel):
    email: Optional[str]
    name: Optional[str]
    surname: Optional[str]


class PersonDelete(PersonBase):
    id: UUID

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    id: UUID
    email: str
    name: Optional[str]
    surname: Optional[str]
    active: bool


class TokenData(BaseModel):
    email: Optional[str] = None


class FinstatCompany(BaseModel):
    Ico: Optional[str]
    Dic: Optional[str]
    IcDPH: Optional[str]
    Name: Optional[str]
    Street: Optional[str]
    StreetNumber: Optional[str]
    ZipCode: Optional[str]
    City: Optional[str]
    District: Optional[str]
    Region: Optional[str]
    Country: Optional[str]
    Activity: Optional[str]
    Created: Optional[str]
    Cancelled: Optional[str]
    Url: Optional[str]
    Revenue: Optional[str]
    RevenueActual: Optional[str]


class EmailSchema(BaseModel):
    email: List[EmailStr]
    body: Dict[str, Any]


class PersonsUUIDList(BaseModel):
    persons: List[UUID]


class BeneficiaryBase(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    company_id: UUID

    class Config:
        orm_mode = True


class Beneficiary(BeneficiaryBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True


class Company(CompanyBase):
    id: UUID
    addresses: List[Address] = []
    persons: List[Person] = []
    beneficiaries: List[Beneficiary] = []

    class Config:
        orm_mode = True
