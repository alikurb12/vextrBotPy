from .start import router as start_router
from .help import router as help_router

def get_all_routers():
    return [
        start_router,
        help_router
    ]