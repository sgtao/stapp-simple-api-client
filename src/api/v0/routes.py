from fastapi import APIRouter

from .config_controller import router as config_router
from .hello import router as hello

from .message_controller import router as message_router
from .service_controller import router as service_router

router = APIRouter()
router.include_router(config_router)
router.include_router(hello)
router.include_router(message_router)
router.include_router(service_router)
