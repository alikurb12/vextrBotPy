from sqladmin import ModelView
from database.models.trades.models import Trades

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