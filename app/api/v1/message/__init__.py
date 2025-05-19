from .views import router as router_message

from fastapi import APIRouter


router = APIRouter()

router.include_router(router_message, prefix='/message')
