from sqladmin import ModelView
from database.models.users.models import Users

class UserAdmin(ModelView, model=Users):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_list = [
        Users.user_id,
        Users.username,
        Users.exchange,
        Users.api_key,
        Users.secret_key,
        Users.subscription_type,
    ]