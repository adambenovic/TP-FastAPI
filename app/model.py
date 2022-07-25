from sqlalchemy import Column, ForeignKey, String, DateTime, func, Integer, Text, Boolean
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Address(Base):
    __tablename__ = "address"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    city = Column(String)
    street = Column(String)
    number = Column(String)
    zip = Column(String)
    company_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('company.id'), nullable=True)
    company = relationship("Company", back_populates="addresses")
    person_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('person.id'), nullable=True)
    person = relationship("Person", back_populates="address")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Company(Base):
    __tablename__ = "company"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    addresses = relationship("Address", back_populates="company", cascade="all, delete")
    id_number = Column(String)
    dic = Column(String)
    registry = Column(String)
    statute = Column(String)
    persons = relationship("Person", back_populates="company")
    beneficiaries = relationship("Beneficiary", back_populates="company")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    finstat_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Integer, default=1)


class Person(Base):
    __tablename__ = "person"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String)
    name = Column(String)
    surname = Column(String)
    country = Column(String)
    id_number = Column(String)
    document_type = Column(String)
    document_number = Column(String)
    document_front = Column(Text)
    document_back = Column(Text)
    document_verification_photo = Column(Text)
    address = relationship("Address", back_populates="person", cascade="all, delete")
    company_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('company.id'))
    company = relationship("Company", back_populates="persons")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    requested_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Beneficiary(Base):
    __tablename__ = "beneficiary"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String)
    surname = Column(String)
    company_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('company.id'))
    company = relationship("Company", back_populates="beneficiaries")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class User(Base):
    __tablename__ = "user"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    email = Column(String)
    password = Column(Text)
    active = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reset_tokens = relationship("ResetToken", back_populates="user")


class ResetToken(Base):
    __tablename__ = "reset_token"

    token = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship("User", back_populates="reset_tokens")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
