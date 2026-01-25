from .start import router as start_router
from .help import router as help_router
from .reset_me import router as reset_router

def get_all_routers():
    return [
        start_router,
        help_router,
        reset_router,
    ]