from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.contracts import RecognitionResponse
from app.security.auth import get_current_user
from app.services.face_service import face_service

router = APIRouter(prefix="/recognition", tags=["recognition"])


@router.post("/identify", response_model=RecognitionResponse)
async def identify(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
) -> RecognitionResponse:
    frame = await face_service.read_image(image)
    return face_service.recognize(db, frame, persist_attendance=False, user=user)


@router.post("/attendance", response_model=RecognitionResponse)
async def attendance(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
) -> RecognitionResponse:
    frame = await face_service.read_image(image)
    return face_service.recognize(db, frame, persist_attendance=True, user=user)

