from sqladmin import ModelView
from database.models.successful_trades.models import SuccessfulTrades

class SuccessTradesAdmin(ModelView, model=SuccessfulTrades):
    name = "Успешная сделка"
    name_plural = "Успешние сделки"
    icon = "fa-solid fa-shield"
    column_list = [
        SuccessfulTrades.id,
        SuccessfulTrades.exchange,
        SuccessfulTrades.ema_fast,
        SuccessfulTrades.atr,
        SuccessfulTrades.bb_lower,
        SuccessfulTrades.ema_fast,
        SuccessfulTrades.ema_slow,
        SuccessfulTrades.closed_at,
        SuccessfulTrades.created_at,
        SuccessfulTrades.entry_price,
        SuccessfulTrades.macd,
        SuccessfulTrades.macd_signal,
    ]