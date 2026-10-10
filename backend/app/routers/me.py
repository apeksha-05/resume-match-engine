import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_user_id

router = APIRouter()


class MeOut(BaseModel):
    user_id: uuid.UUID


@router.get("/me", response_model=MeOut)
def get_me(user_id: uuid.UUID = Depends(get_current_user_id)) -> MeOut:
    return MeOut(user_id=user_id)