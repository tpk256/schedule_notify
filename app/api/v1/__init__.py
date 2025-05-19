from fastapi import APIRouter

from .token import router as token_router
from .group import router as group_router
from .message import router as message_router


router = APIRouter()

router.include_router(token_router, prefix='/v1')
router.include_router(group_router, prefix='/v1')
router.include_router(message_router, prefix='/v1')
