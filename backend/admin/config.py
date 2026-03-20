from sqladmin import Admin
from backend.admin.models.user import UserAdmin
from backend.admin.models.trade import TradesAdmin

def configure_admin_routes(admin : Admin):
    admin.add_view(UserAdmin)
    admin.add_view(TradesAdmin)