import datetime
import logging
from database.models.trades.dao import TradesDAO
from database.models.users.dao import UsersDAO
from database.models.successful_trades.dao import SuccessfulTradesDAO

log = logging.getLogger(__name__)

async def save_successful_trades(
    symbol: str,
    rsi=None, macd=None, macd_signal=None,
    atr=None, ema_fast=None, ema_slow=None,
    volume=None, timeframe=None,
):
    """
    Вызывается когда приходит MOVE_SL — значит TP1 сработал.
    Сохраняем сделку в successful_trades для датасета ML.
    """
    try:
        # Нормализуем символ как в OKX router
        symbol_okx = symbol.replace(".P", "").replace("USDT", "-USDT") + "-SWAP"
        symbol_bingx = symbol.replace(".P", "").replace("USDT", "-USDT")

        users = await UsersDAO.get_all()
        if not users:
            return

        for user in users:
            # Определяем символ в зависимости от биржи
            sym = symbol_okx if user.exchange == "OKX" else symbol_bingx

            trades = await TradesDAO.get_all(
                user_id=user.user_id,
                symbol=sym,
                status="open"
            )
            if not trades:
                continue

            for trade in trades:
                try:
                    # Считаем доп. признаки для ML
                    sl_distance_pct = None
                    tp1_distance_pct = None
                    risk_reward = None

                    if trade.entry_price and trade.stop_loss:
                        sl_distance_pct = abs(trade.entry_price - trade.stop_loss) / trade.entry_price * 100

                    if trade.entry_price and trade.take_profit_1:
                        tp1_distance_pct = abs(trade.take_profit_1 - trade.entry_price) / trade.entry_price * 100

                    if sl_distance_pct and tp1_distance_pct and sl_distance_pct > 0:
                        risk_reward = tp1_distance_pct / sl_distance_pct

                    await SuccessfulTradesDAO.add(
                        user_id=user.user_id,
                        trade_id=trade.trade_id,
                        symbol=trade.symbol,
                        side=trade.side,
                        exchange=trade.exchange,
                        timeframe=timeframe,
                        entry_price=trade.entry_price,
                        stop_loss=trade.stop_loss,
                        take_profit_1=trade.take_profit_1,
                        take_profit_2=trade.take_profit_2,
                        take_profit_3=trade.take_profit_3,
                        quantity=trade.quantity,
                        tps_hit=1,  # минимум 1 TP сработал
                        pnl=trade.pnl,
                        pnl_percent=trade.pnl_percent,
                        created_at=trade.created_at,
                        closed_at=datetime.datetime.now(),
                        rsi=rsi,
                        ema_fast=ema_fast,
                        ema_slow=ema_slow,
                        volume=volume,
                        atr=atr,
                        macd=macd,
                        macd_signal=macd_signal,
                        sl_distance_pct=sl_distance_pct,
                        tp1_distance_pct=tp1_distance_pct,
                        risk_reward=risk_reward,
                    )
                    log.info(f"✅ Успешная сделка сохранена: trade_id={trade.trade_id} symbol={sym}")

                except Exception as e:
                    log.error(f"Ошибка сохранения successful_trade для trade_id={trade.trade_id}: {e}")

    except Exception as e:
        log.error(f"Ошибка в save_successful_trades: {e}")
