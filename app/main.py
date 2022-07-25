import os

from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse

load_dotenv()

from app.repository import add_system_user
from app.user_service import user_management_service
from app.auth_utils import get_current_user, create_access_token
from datetime import datetime
from typing import List
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import repository, deepfaceService
from app import model
from app import schema
from app import finstat
from app.database import engine, Base, get_db
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID
from pydantic import EmailStr
from app import email_sender

Base.metadata.create_all(bind=engine)


add_system_user()
app = FastAPI(debug=eval(os.environ["BE_STACK_TRACE_ERROR"]))
app.include_router(deepfaceService.app)
app.include_router(user_management_service.app)
origins = [
    "http://localhost:5000",
    "http://pumec.zapto.org:5000",
    "http://klyck-dev-app-fe.azurewebsites.net",
    "https://klyck-dev-app-fe.azurewebsites.net",
    "http://klyck-dev-app-fe-cloud-db.azurewebsites.net",
    "https://klyck-dev-app-fe-cloud-db.azurewebsites.net",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def authenticate_user(db, email: str, password: str):
    user = repository.get_user_by_email_active(db, email)
    if user is None:
        return False
    if not repository.verify_password(password, user.password):
        return False
    return user


@app.post("/token", response_model=schema.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer", "id": user.id, "email": user.email, "name": user.name, "surname": user.surname, "active": user.active}


@app.get("/")
def alive(request: Request):
    return {"message": "Server is online", "root_path": request.scope.get("root_path")}


@app.post("/company", response_model=schema.Company)
def create_company(company: schema.CompanyBase, db: Session = Depends(get_db),
                   current_user: model.User = Depends(get_current_user)):
    db_company = repository.get_company_by_id_number(db, id_number=company.id_number)
    if db_company:
        raise HTTPException(status_code=400, detail="Company with same ID Number already exists!")
    return repository.create_company(db=db, company=company)


@app.get("/company", response_model=List[schema.Company])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                   current_user: model.User = Depends(get_current_user)):
    return repository.get_companies(db, skip=skip, limit=limit)


@app.get("/company/{company_id}", response_model=schema.Company)
def read_company(company_id: UUID, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    db_company = repository.get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found.")
    return db_company


@app.get("/company/{company_id}/address", response_model=List[schema.Address])
def get_company_addresses(company_id: UUID, db: Session = Depends(get_db),
                          current_user: model.User = Depends(get_current_user)):
    return repository.get_addresses_by_company(db=db, company_id=company_id)


@app.get("/company/{company_id}/aml", response_class=PlainTextResponse)
def get_company_aml(company_id: UUID, db: Session = Depends(get_db),
                          current_user: model.User = Depends(get_current_user)):
    db_company = repository.get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found.")

    if db_company.status == 1:
        raise HTTPException(status_code=404, detail="Company can not complete AML procedure without beneficiaries.")

    if db_company.status == 2:
        db_company.status = 3
        db.commit()

    return "OK"


@app.post("/person", response_model=schema.Person)
def create_person(person: schema.PersonCreate, db: Session = Depends(get_db),
                  current_user: model.User = Depends(get_current_user)):
    return repository.create_person(db=db, person=person)


@app.get("/person", response_model=List[schema.Person])
def read_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                 current_user: model.User = Depends(get_current_user)):
    return repository.get_persons(db, skip=skip, limit=limit)


@app.get("/person/{person_id}", response_model=schema.Person)
def read_person(person_id: UUID, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    db_person = repository.get_person(db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found.")
    return db_person


@app.post("/person/{person_id}/update", response_model=schema.Person)
def update_person(person_id: UUID, person: schema.PersonUpdate, db: Session = Depends(get_db),
                  current_user: model.User = Depends(get_current_user)):
    db_person = repository.update_person(db=db, person_id=person_id, person=person)

    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found.")

    return db_person


@app.delete("/person/{person_id}/delete", response_class=PlainTextResponse)
def delete_person(person_id: UUID, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    db_person = repository.get_person(db, person_id=person_id)

    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found.")

    repository.delete_person(db=db, person=db_person)

    return


@app.get("/person/{person_id}/address", response_model=List[schema.Address])
def get_person_addresses(person_id: UUID, db: Session = Depends(get_db),
                         current_user: model.User = Depends(get_current_user)):
    return repository.get_addresses_by_person(db=db, person_id=person_id)

@app.get("/finstat/company/{ico}", response_model=schema.FinstatCompany)
async def get_company_finstat_data(ico: str, current_user: model.User = Depends(get_current_user)):
    if len(ico) < 6 or len(ico) > 8:
        raise HTTPException(status_code=400, detail="ICO Too short.")

    return await finstat.find_company_by_ico(ico)


@app.get("/app/check/{person_id}", response_model=schema.PersonCheck)
def check_person_for_app(person_id: UUID, db: Session = Depends(get_db)):
    db_person = repository.get_person(db, person_id=person_id)

    if db_person is None:
        raise HTTPException(status_code=404, detail="Person does not exist.")

    if db_person.verified_at is not None:
        raise HTTPException(status_code=403, detail="Can not be verified again.")

    person_companies = repository.get_person_companies(db, person=db_person)
    person_check = schema.PersonCheck(
        id=str(db_person.id)
    )

    for company in person_companies:
        company_check = schema.CompanyCheck()
        company_check.name = company.name
        company_check.id_number = company.id_number
        person_check.companies.append(company_check)

    if not person_check.companies:
        raise HTTPException(status_code=404, detail="Person has no company.")

    return person_check


@app.post("/app/verify", response_model=schema.Person)
async def verify_person(person: schema.PersonVerify, db: Session = Depends(get_db)):
    db_person = repository.get_person(db, person.id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person with specified ID does not exist!")

    if db_person.verified_at is not None:
        raise HTTPException(status_code=403, detail="Person already verified!")

    person = repository.verify_person(db=db, db_person=db_person, person=person)
    await email_sender.send_verification_confirm_mail(db_person.email)

    return person


@app.get("/person/request/{person_id}/{language}", response_class=PlainTextResponse)
async def request_verification(person_id: UUID, language: str, db: Session = Depends(get_db),
                               current_user: model.User = Depends(get_current_user)):
    db_person = repository.get_person(db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Person not found.")

    if db_person.verified_at is not None:
        raise HTTPException(status_code=403, detail="Person already verified.")

    await send_kyc_email(db_person, language, db)

    return


@app.get("/person/request/all/{company_id}/{language}", response_class=PlainTextResponse)
async def request_verification_by_all_company_persons(company_id: UUID, language: str, db: Session = Depends(get_db),
                                                      current_user: model.User = Depends(get_current_user)):
    db_company = repository.get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found.")

    for db_person in db_company.persons:
        if db_person.verified_at is None:
            await send_kyc_email(db_person, language, db)

    return


@app.post("/person/request/persons/{company_id}/{language}", response_class=PlainTextResponse)
async def request_verification_by_company_and_persons(company_id: UUID, language: str,
                                                      company_persons: schema.PersonsUUIDList,
                                                      db: Session = Depends(get_db),
                                                      current_user: model.User = Depends(get_current_user)):
    db_company = repository.get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found.")

    for person_id in company_persons.persons:
        db_person = repository.get_person_by_company_and_id(db, company_id=company_id, person_id=person_id)
        if db_person is not None and db_person.verified_at is None:
            await send_kyc_email(db_person, language, db)

    return


async def send_kyc_email(db_person, language, db):
    email_str = [EmailStr(db_person.email)]
    body = {"link": 'http://pumec.zapto.org:8080/login?token=' + str(db_person.id)}
    email = schema.EmailSchema(email=email_str, body=body)
    await email_sender.send_email_async('KYC identification', email, template_name='email_kyc_' + language + '.html')
    db_person.requested_at = datetime.now()
    db.commit()
    db.refresh(db_person)
    company = repository.get_company(db,db_person.company_id)
    if company.status == 3:
        company.status = 4
    db.commit()


@app.post("/beneficiary", response_model=schema.Beneficiary)
def create_beneficiary(beneficiary: schema.BeneficiaryBase, db: Session = Depends(get_db)):
    db_beneficiary = repository.get_beneficiary_by_name_surname_company(db, beneficiary.name, beneficiary.surname,
                                                                        beneficiary.company_id)

    if db_beneficiary:
        raise HTTPException(status_code=400, detail="Beneficiary already exists.")

    return repository.create_beneficiary(db=db, beneficiary=beneficiary)


@app.get("/beneficiary", response_model=List[schema.Beneficiary])
def read_beneficiaries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                       current_user: model.User = Depends(get_current_user)):
    return repository.get_beneficiaries(db, skip=skip, limit=limit)


@app.get("/beneficiary/{beneficiary_id}", response_model=schema.Beneficiary)
def read_beneficiary(beneficiary_id: UUID, db: Session = Depends(get_db), current_user: model.User = Depends(
    get_current_user)):
    db_beneficiary = repository.get_beneficiary(db, beneficiary_id=beneficiary_id)

    if db_beneficiary is None:
        raise HTTPException(status_code=404, detail="Beneficiary not found.")

    return db_beneficiary


@app.delete("/beneficiary/{beneficiary_id}/delete", response_class=PlainTextResponse)
def delete_beneficiary(beneficiary_id: UUID, db: Session = Depends(get_db), current_user: model.User = Depends(
    get_current_user)):
    db_beneficiary = repository.get_beneficiary(db, beneficiary_id=beneficiary_id)

    if db_beneficiary is None:
        raise HTTPException(status_code=404, detail="Beneficiary not found.")

    repository.delete_beneficiary(db=db, beneficiary=db_beneficiary)

    return


@app.get("/search", response_model=List[schema.Company])
def search_companies(q: str, db: Session = Depends(get_db),
                     current_user: model.User = Depends(get_current_user)):
    if not q:
        raise HTTPException(status_code=400, detail="You must specify q url parameter in order to search companies.")

    companies = repository.search_companies(db, q)
    companies_by_persons = repository.search_companies_by_persons(db, q)
    companies_by_beneficiaries = repository.search_companies_by_beneficiaries(db, q)

    return list(set(companies + companies_by_persons + companies_by_beneficiaries))
