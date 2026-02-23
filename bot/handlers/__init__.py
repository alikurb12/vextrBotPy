from .start import router as start_router
from .help import router as help_router
from .reset_me import router as reset_router
from .registration import router as registration_router
from .moderation import router as moderation_router
from .my_status import router as my_status_router
from .main_menu import router as main_menu_router
from .process_email import router as process_email_router
from .get_payment import router as get_payment_router
from .check_payment import router as check_payment_router
from .process_promo_code import router as process_promo_code_router
from .process_exchange_selection import router as process_exchange_selection_router
from .get_my_positions import router as get_my_positions_router


def get_all_routers():
    return [
        start_router,
        help_router,
        reset_router,
        registration_router,
        moderation_router,
        my_status_router,
        main_menu_router,
        get_payment_router,
        check_payment_router,
        process_email_router,
        process_promo_code_router,
        process_exchange_selection_router,
        get_my_positions_router,
    ]