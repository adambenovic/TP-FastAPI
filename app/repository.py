import os
from datetime import datetime
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import model
from app import schema
from app.database import get_db
from app.or_scraper.scraper import get_names
from app.user_service.schema_user import UserCreate, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_address(db: Session, address_id: UUID):
    return db.query(model.Address).filter(model.Address.id == address_id).first()


def get_addresses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Address).offset(skip).limit(limit).all()


def create_address(db: Session, address: schema.AddressCreate, company=None, person=None):
    db_address = model.Address(
        city=address.city,
        street=address.street,
        number=address.number,
        company_id=company,
        person_id=person
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def get_addresses_by_person(db: Session, person_id: UUID):
    return db.query(model.Address).filter(model.Address.person_id == person_id).all()


def get_addresses_by_company(db: Session, company_id: UUID):
    return db.query(model.Address).filter(model.Address.company_id == company_id).all()


def get_company(db: Session, company_id: UUID) -> model.Company:
    return db.query(model.Company).filter(model.Company.id == company_id).first()


def get_company_by_id_number(db: Session, id_number: str):
    return db.query(model.Company).filter(model.Company.id_number == id_number).first()


def get_companies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Company).offset(skip).limit(limit).all()


def create_company(db: Session, company: schema.CompanyBase):
    db_company = model.Company(
        name=company.name,
        id_number=company.id_number,
        registry=company.registry,
        statute=company.status,
        dic=company.dic
    )

    if company.address:
        address = create_address(db, company.address)
        db_company.addresses = [address]

    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    scrape_persons_for_company(db, db_company)

    return db_company


def get_person(db: Session, person_id: UUID) -> model.Person:
    return db.query(model.Person).filter(model.Person.id == person_id, model.Person.deleted_at == None).first()


def get_beneficiary(db: Session, beneficiary_id: UUID):
    return db.query(model.Beneficiary).filter(model.Beneficiary.id == beneficiary_id, model.Beneficiary.deleted_at == None).first()


def delete_person(db: Session, person: model.Person):
    person.deleted_at = datetime.now()
    db.commit()

    return


def delete_beneficiary(db: Session, beneficiary: model.Beneficiary):
    beneficiary.deleted_at = datetime.now()
    db.commit()

    beneficiaries = db.query(model.Company).join(model.Company.beneficiaries, aliased=True)\
        .filter(model.Company.id == beneficiary.company.id, model.Beneficiary.deleted_at == None)

    if beneficiaries.count() == 0:
        beneficiary.company.status = 1
        db.commit()

    return


def get_beneficiary_by_name_surname_company(db: Session, name: str, surname: str, company_id: UUID):
    return db.query(model.Beneficiary).filter(model.Beneficiary.name == name, model.Beneficiary.surname == surname,
                                              model.Beneficiary.company_id == company_id,
                                              model.Beneficiary.deleted_at == None).first()

def get_person_companies(db: Session, person: schema.Person):
    return db.query(model.Company).join(model.Company.persons, aliased=True).filter(model.Person.id == person.id,
                                                                                    model.Person.deleted_at == None)


def get_person_by_company_and_id(db: Session, company_id: UUID, person_id: UUID):
    return db.query(model.Person).filter(model.Person.id == person_id, model.Person.deleted_at == None,
                                         model.Person.company_id == company_id).first()


def get_person_by_id_number(db: Session, id_number: str):
    return db.query(model.Person).filter(model.Person.id_number == id_number, model.Person.deleted_at == None).first()


def get_persons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Person).filter(model.Person.deleted_at == None).offset(skip).limit(limit).all()


def create_person(db: Session, person: schema.PersonCreate):
    db_person = model.Person(
        email=person.email,
        name=person.name,
        surname=person.surname,
        country=person.country,
        id_number=person.id_number,
        document_type=person.document_type,
        document_number=person.document_number,
        document_front=person.document_front,
        document_back=person.document_back,
        document_verification_photo=person.document_verification_photo
    )

    if person.company is not None:
        db_company = get_company(db, person.company)

        if db_company is not None:
            db_person.company = db_company

            if db_company.status == 5:
                db_company.status = 4

    if person.address is not None:
        address = create_address(db, person.address)
        db_person.address = [address]

    db.add(db_person)
    db.commit()
    db.refresh(db_person)

    return db_person


def update_person(person_id: UUID, db: Session, person: schema.PersonUpdate):
    db_person = get_person(db, person_id)

    if db_person is None:
        return None

    if person.email is not None:
        db_person.email = person.email

    if person.name is not None:
        db_person.name = person.name

    if person.surname is not None:
        db_person.surname = person.surname

    db.commit()
    db.refresh(db_person)

    return db_person


def verify_person(db: Session, db_person: schema.Person, person: schema.PersonVerify):
    address = create_address(db, person.address)
    db_person.name = person.name
    db_person.surname = person.surname
    db_person.country = person.country
    db_person.id_number = person.id_number
    db_person.document_type = person.document_type
    db_person.document_number = person.document_number
    db_person.document_front = person.document_front
    db_person.document_back = person.document_back
    db_person.document_verification_photo = person.document_verification_photo
    db_person.address = [address]
    db_person.verified_at = datetime.now()

    db.commit()
    all_verified = True
    company = get_company(db, db_person.company_id)

    for p in company.persons:
        if p.verified_at is None and p.deleted_at is None:
            all_verified = False

    if all_verified and company.status == 4:
        company.status = 5

    db.commit()
    db.refresh(db_person)

    return db_person


def get_beneficiaries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Beneficiary).filter(model.Beneficiary.deleted_at == None).offset(skip).limit(limit).all()


def create_beneficiary(db: Session, beneficiary: schema.BeneficiaryBase):
    db_beneficiary = model.Beneficiary(
        name=beneficiary.name,
        surname=beneficiary.surname
    )

    if beneficiary.company_id is not None:
        db_company = get_company(db, beneficiary.company_id)

        if db_company is not None:
            db_beneficiary.company_id = db_company.id
            db_beneficiary.company = db_company
            db_company.status = 2

    db.add(db_beneficiary)
    db.commit()
    db.refresh(db_beneficiary)

    return db_beneficiary


def get_user_by_email(db: Session, email: str):
    return db.query(model.User).filter(model.User.email == email).first()


def get_user_by_email_active(db: Session, email: str):
    user = get_user_by_email(db, email)

    if user is not None and user.active is True:
        return user

    return None


def get_user_by_id(db: Session, user_id: UUID) -> model.User:
    return db.query(model.User).filter(model.User.id == user_id).first()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(db: Session, user: UserCreate):
    db_user = model.User(
        email=user.email,
        name=user.name,
        surname=user.surname,
        password=get_password_hash(user.password),
        active=False
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def write_finstat_company_data(company: model.Company, finstat: schema.FinstatCompany):
    company.name = finstat.Name
    company.id_number = finstat.Ico
    company.dic = finstat.Dic
    address = model.Address(
        city=finstat.City,
        street=finstat.Street,
        number=finstat.StreetNumber,
        zip=finstat.ZipCode,
    )
    company.addresses = [address]

    return company


def search_companies(db: Session, query: str):
    return db.query(model.Company).filter(model.Company.id_number.ilike(f'%{query}%')
                                          | model.Company.name.ilike(f'%{query}%')
                                          | model.Company.dic.ilike(f'%{query}%')
                                          ).all()


def search_companies_by_persons(db: Session, query: str):
    return db.query(model.Company).join(model.Company.persons) \
        .filter(model.Company.persons.property.mapper.class_.deleted_at == None,
                model.Company.persons.property.mapper.class_.id_number.ilike(f'%{query}%')
                | model.Company.persons.property.mapper.class_.email.ilike(f'%{query}%')
                | model.Company.persons.property.mapper.class_.name.ilike(f'%{query}%')
                | model.Company.persons.property.mapper.class_.surname.ilike(f'%{query}%')
                ).all()


def search_companies_by_beneficiaries(db: Session, query: str):
    return db.query(model.Company).join(model.Company.beneficiaries) \
        .filter(model.Company.beneficiaries.property.mapper.class_.deleted_at == None,
                model.Company.beneficiaries.property.mapper.class_.name.ilike(f'%{query}%')
                | model.Company.beneficiaries.property.mapper.class_.surname.ilike(f'%{query}%')
                ).all()


def get_users(db):
    return db.query(model.User).all()


def update_user_validity(db: Session, user_id, new_state):
    db_user = get_user_by_id(db, user_id)

    if db_user is None:
        raise NoResultFound()

    if db_user.active == new_state:
        return

    db_user.active = new_state
    db.commit()

    return


def add_system_user():
    print("CHECK FOR SYS ADMIN")
    db = next(get_db())
    users = get_users(db)
    if len(users) == 0:
        print("CREATING SYS ADMIN")
        user = UserCreate(**{"email": os.environ["ADMIN_MAIL"], "name": "SYSTEM", "surname": "ADMIN",
                             "password": os.environ["ADMIN_PASSWORD"], })

        update_user_validity(db, create_user(db, user).id, True)
        print("SYS ADMIN CREATED")
    return


def scrape_persons_for_company(db: Session, company: model.Company):
    person_list = get_names(company.id_number)
    for p in person_list:
        p = p.split(" ")
        create_person(db, schema.PersonCreate(**{"name": " ".join(p[:-1]), "surname": p[-1], "company": company.id}))


def create_reset_token(db: Session, user: User):
    token = model.ResetToken(
        user=user,
    )

    db.add(token)
    db.commit()
    db.refresh(token)

    return token


def get_reset_token(db: Session, token: UUID):
    return db.query(model.ResetToken).filter(model.ResetToken.token == token, model.ResetToken.used_at == None).first()


def update_user_password(db: Session, user: User, new_password: str):
    user.password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)

    return user
