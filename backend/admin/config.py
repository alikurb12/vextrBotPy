from sqladmin import Admin
from backend.admin.models.user import UserAdmin
from backend.admin.models.trade import TradesAdmin
from backend.admin.models.success_trade import SuccessTradesAdmin

def configure_admin_routes(admin : Admin):
    admin.add_view(UserAdmin)
    admin.add_view(TradesAdmin)
    admin.add_view(SuccessTradesAdmin)