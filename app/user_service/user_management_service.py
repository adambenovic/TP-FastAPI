from typing import List
from uuid import UUID
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.responses import PlainTextResponse
from datetime import datetime
from pydantic import EmailStr
import os
from app import repository, model
from app.auth_utils import get_current_user
from app.database import get_db
from app.user_service.schema_user import User, UserCreate, ResetPassword, UpdatePassword
from app import schema
from app import email_sender


app = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)


@app.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = repository.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return repository.create_user(db=db, user=user)


@app.get("s", response_model=List[User])
def read_users(db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    return repository.get_users(db)


@app.get("/{user_id}", response_model=User)
def read_users(user_id: UUID, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    db_user = repository.get_user_by_id(db, user_id=user_id)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return db_user


@app.post("/update-validity", response_class=PlainTextResponse)
def update_user_valid(user_id: UUID, new_valid_state: bool, db: Session = Depends(get_db),
                  current_user: model.User = Depends(get_current_user)):
    try:
        repository.update_user_validity(db=db, user_id=user_id, new_state=new_valid_state)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found.")

    return "OK"


@app.post("/reset-password", response_class=PlainTextResponse)
async def reset_password(reset_password: ResetPassword, db: Session = Depends(get_db)):
    db_user = repository.get_user_by_email(db, email=reset_password.email)

    if db_user is None:
        raise HTTPException(status_code=400, detail="Error.")

    token = repository.create_reset_token(db=db, user=db_user)
    email_str = [EmailStr(reset_password.email)]
    body = {"link": os.environ["FRONTEND_RESET_PASSWORD_URL"] + '?token=' + str(token.token)}
    email = schema.EmailSchema(email=email_str, body=body)
    await email_sender.send_email_async('Reset password', email, template_name='email_reset_password_' + reset_password.language + '.html')

    return "OK"


@app.post("/update-password", response_model=User)
def update_password(update_password: UpdatePassword, db: Session = Depends(get_db)):
    reset_token = repository.get_reset_token(db=db, token=update_password.token)

    if reset_token is None:
        raise HTTPException(status_code=404, detail="Token invalid.")

    reset_token.used_at = datetime.now()
    db.commit()

    return repository.update_user_password(db=db, user=reset_token.user, new_password=update_password.password)
