from .views import router as router_group

from fastapi import APIRouter


router = APIRouter()

router.include_router(router_group, prefix='/group')
