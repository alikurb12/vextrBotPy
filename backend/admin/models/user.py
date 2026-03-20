from database.models.users.models import Users
from sqladmin import ModelView

class UserAdmin(ModelView, model=Users):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    column_list = [
        Users.user_id,
        Users.username,
        Users.exchange,
        Users.api_key,
        Users.secret_key,
        Users.subscription_type,
    ]
