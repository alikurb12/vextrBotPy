from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from database.models.trades.dao import TradesDAO
from database.models.users.dao import UsersDAO
import keyboards.keyboards as kb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import datetime

router = Router()

@router.callback_query(F.data == "statistics")
async def show_statistics(callback_query: CallbackQuery):
    await callback_query.answer()
    
    trades = await TradesDAO.get_all(user_id=callback_query.from_user.id)
    
    if not trades:
        await callback_query.message.answer("📊 У вас пока нет сделок для анализа.")
        return

    closed_trades = [t for t in trades if t.status in ("closed", "sl_moved_to_breakeven") and t.pnl is not None]
    open_trades = [t for t in trades if t.status == "open"]
    
    total = len(closed_trades)
    wins = len([t for t in closed_trades if t.pnl and t.pnl > 0])
    losses = len([t for t in closed_trades if t.pnl and t.pnl <= 0])
    winrate = (wins / total * 100) if total > 0 else 0
    total_pnl = sum(t.pnl for t in closed_trades if t.pnl)
    avg_win = sum(t.pnl for t in closed_trades if t.pnl and t.pnl > 0) / wins if wins > 0 else 0
    avg_loss = sum(t.pnl for t in closed_trades if t.pnl and t.pnl < 0) / losses if losses > 0 else 0
    best = max((t.pnl for t in closed_trades if t.pnl), default=0)
    worst = min((t.pnl for t in closed_trades if t.pnl), default=0)

    text = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"📈 Всего сделок: <b>{total}</b>\n"
        f"✅ Прибыльных: <b>{wins}</b>\n"
        f"❌ Убыточных: <b>{losses}</b>\n"
        f"🎯 Винрейт: <b>{winrate:.1f}%</b>\n\n"
        f"💰 Общий P&L: <b>{total_pnl:+.2f} USDT</b>\n"
        f"📉 Средняя прибыль: <b>{avg_win:+.2f} USDT</b>\n"
        f"📉 Средний убыток: <b>{avg_loss:+.2f} USDT</b>\n"
        f"🏆 Лучшая сделка: <b>{best:+.2f} USDT</b>\n"
        f"💀 Худшая сделка: <b>{worst:+.2f} USDT</b>\n\n"
        f"🔓 Открытых сделок: <b>{len(open_trades)}</b>"
    )

    await callback_query.message.answer(text, parse_mode="HTML", reply_markup=kb.statistics_kb)

    # График equity curve
    if closed_trades:
        sorted_trades = sorted(closed_trades, key=lambda t: t.closed_at or t.created_at)
        cumulative = []
        total_sum = 0
        dates = []
        for t in sorted_trades:
            total_sum += t.pnl or 0
            cumulative.append(total_sum)
            dates.append(t.closed_at or t.created_at)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.patch.set_facecolor('#1a1a2e')

        # Equity curve
        ax1.set_facecolor('#16213e')
        color = '#00ff88' if cumulative[-1] >= 0 else '#ff4444'
        ax1.plot(dates, cumulative, color=color, linewidth=2)
        ax1.fill_between(dates, cumulative, alpha=0.3, color=color)
        ax1.axhline(y=0, color='white', linestyle='--', alpha=0.3)
        ax1.set_title('Equity Curve', color='white', fontsize=14)
        ax1.tick_params(colors='white')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        for spine in ax1.spines.values():
            spine.set_edgecolor('#333366')

        # P&L по сделкам (бары)
        ax2.set_facecolor('#16213e')
        pnls = [t.pnl or 0 for t in sorted_trades]
        bar_colors = ['#00ff88' if p >= 0 else '#ff4444' for p in pnls]
        ax2.bar(range(len(pnls)), pnls, color=bar_colors, alpha=0.8)
        ax2.axhline(y=0, color='white', linestyle='--', alpha=0.3)
        ax2.set_title('P&L по сделкам', color='white', fontsize=14)
        ax2.tick_params(colors='white')
        for spine in ax2.spines.values():
            spine.set_edgecolor('#333366')

        plt.tight_layout(pad=2.0)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                    facecolor='#1a1a2e')
        buf.seek(0)
        plt.close()

        photo = BufferedInputFile(buf.read(), filename="statistics.png")
        await callback_query.message.answer_photo(
            photo=photo,
            caption="📈 Ваши графики"
        )
