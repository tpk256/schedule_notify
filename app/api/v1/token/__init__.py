from fastapi import APIRouter

from .views import router as token_router


router = APIRouter()

router.include_router(token_router, prefix='/token')
