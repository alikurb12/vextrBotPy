from sqladmin import Admin

def configure_admin_routes(admin : Admin):
    from backend.admin.models import UserAdmin
    admin.add_view(UserAdmin)