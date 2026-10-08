from fastapi import APIRouter, Depends, File, UploadFile

from app.schemas.contracts import LivenessOut
from app.security.auth import get_current_user
from app.services.face_service import face_service

router = APIRouter(prefix="/liveness", tags=["liveness"])


@router.post("/check", response_model=LivenessOut)
async def check_liveness(image: UploadFile = File(...), _: str = Depends(get_current_user)) -> LivenessOut:
    frame = await face_service.read_image(image)
    faces = face_service.engine.embed_faces(frame)
    result = face_service.liveness.evaluate(frame, faces[0].box if faces else None)
    return LivenessOut(**result.__dict__)

