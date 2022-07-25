from uuid import UUID

from deepface import DeepFace
from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import repository
from app.database import get_db

app = APIRouter(
    prefix="/facecheck",
    tags=["FaceCheck"],
    responses={404: {"description": "Not found"}},
)

# DeepFace.build_model("VGG-Face")


class FaceCheck(BaseModel):
    person_foto: str
    document_verification_photo: str


class FaceCheckResponse(BaseModel):
    response: bool


@app.post("/{person_id}", response_model=FaceCheckResponse)
def read_person(images: FaceCheck, person_id: UUID, db: Session = Depends(get_db)):
    db_user = repository.get_person(db, person_id=person_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Person not found.")
    try:
        result = DeepFace.verify(images.person_foto, images.document_verification_photo)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
    r = FaceCheckResponse(response=bool(result['verified']))

    return r
