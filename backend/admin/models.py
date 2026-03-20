from sqladmin import ModelView
from database.models.users.models import Users
from database.models.trades.models import Trades
import markupsafe

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

class TradesAdmin(ModelView, model=Trades):
    name = "Сделка"
    name_plural = "Сделки"
    icon = "fa-solid fa-chart-line"
    column_list = [
        Trades.trade_id,
        Trades.user_id,
        Trades.symbol,
        Trades.side,
        Trades.entry_price,
        Trades.stop_loss,
        Trades.take_profit_1,
        Trades.take_profit_2,
        Trades.take_profit_3,
        Trades.status,
    ]