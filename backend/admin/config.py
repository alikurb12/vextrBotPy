from sqladmin import Admin

def configure_admin_routes(admin : Admin):
    from backend.admin.models import UserAdmin, TradesAdmin
    admin.add_view(UserAdmin)
    admin.add_view(TradesAdmin)