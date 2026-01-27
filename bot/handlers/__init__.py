from .start import router as start_router
from .help import router as help_router
from .reset_me import router as reset_router
from .registration import router as registration_router
from .moderation import router as moderation_router

def get_all_routers():
    return [
        start_router,
        help_router,
        reset_router,
        registration_router,
        moderation_router,
    ]