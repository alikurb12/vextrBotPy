import datetime
import logging
from database.database import async_session_maker
from database.models.trades.models import Trades
from database.models.successful_trades.models import SuccessfulTrades
from sqlalchemy import select

log = logging.getLogger(__name__)

async def save_successful_trades(
    symbol: str,
    rsi=None, macd=None, macd_signal=None,
    atr=None, ema_fast=None, ema_slow=None,
    volume=None, timeframe=None,
):
    try:
        symbol_okx = symbol.replace(".P", "").replace("USDT", "-USDT") + "-SWAP"
        symbol_bingx = symbol.replace(".P", "").replace("USDT", "-USDT")

        # Получаем сделки в одной сессии
        async with async_session_maker() as session:
            result = await session.execute(
                select(Trades).where(
                    Trades.symbol.in_([symbol_okx, symbol_bingx]),
                    Trades.status == "open"
                )
            )
            trades = result.scalars().all()

        if not trades:
            log.info(f"Нет открытых сделок для {symbol}")
            return

        # Сохраняем каждую сделку в отдельной сессии
        for trade in trades:
            try:
                sl_distance_pct = None
                tp1_distance_pct = None
                risk_reward = None

                if trade.entry_price and trade.stop_loss:
                    sl_distance_pct = abs(trade.entry_price - trade.stop_loss) / trade.entry_price * 100

                if trade.entry_price and trade.take_profit_1:
                    tp1_distance_pct = abs(trade.take_profit_1 - trade.entry_price) / trade.entry_price * 100

                if sl_distance_pct and tp1_distance_pct and sl_distance_pct > 0:
                    risk_reward = tp1_distance_pct / sl_distance_pct

                async with async_session_maker() as session:
                    obj = SuccessfulTrades(
                        user_id=trade.user_id,
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
                        tps_hit=1,
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
                    session.add(obj)
                    await session.commit()
                    log.info(f"✅ Успешная сделка сохранена: trade_id={trade.trade_id} symbol={trade.symbol}")

            except Exception as e:
                log.error(f"Ошибка сохранения successful_trade для trade_id={trade.trade_id}: {e}")

    except Exception as e:
        log.error(f"Ошибка в save_successful_trades: {e}")
