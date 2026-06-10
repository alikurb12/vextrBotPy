from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
import keyboards.keyboards as kb
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
VIDEOS_DIR = BASE_DIR / "videos"

router = Router()

@router.callback_query(F.data == "statistics")
async def show_statistics(callback_query: CallbackQuery):
    await callback_query.answer()
    
    total = 156
    wins = 98
    losses = 58
    winrate = 62.8
    total_pnl = 2847.50
    avg_win = 45.30
    avg_loss = -28.15
    best = 124.80
    worst = -72.50

    text = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"📈 Всего сделок: <b>{total}</b>\n"
        f"✅ Прибыльных: <b>{wins}</b>\n"
        f"❌ Убыточных: <b>{losses}</b>\n"
        f"🎯 Винрейт: <b>{winrate:.1f}%</b>\n\n"
        f"💰 Общий P&L: <b>+{total_pnl:,.2f} USDT</b>\n"
        f"📈 Средняя прибыль: <b>+{avg_win:.2f} USDT</b>\n"
        f"📉 Средний убыток: <b>{avg_loss:.2f} USDT</b>\n"
        f"🏆 Лучшая сделка: <b>+{best:.2f} USDT</b>\n"
        f"💀 Худшая сделка: <b>{worst:.2f} USDT</b>\n\n"
    )

    await callback_query.message.answer(text, parse_mode="HTML", reply_markup=kb.statistics_kb)

    possible_names = ["statistics.png", "statistics_graph.png", "stats.png", "graph.png"]
    found_graph = None
    
    for name in possible_names:
        graph_path = VIDEOS_DIR / name
        print(f"Проверяем: {graph_path} - Существует: {os.path.exists(graph_path)}")
        if os.path.exists(graph_path):
            found_graph = graph_path
            break
    
    if not found_graph:
        for name in possible_names:
            graph_path = BASE_DIR / name
            print(f"Проверяем корень: {graph_path} - Существует: {os.path.exists(graph_path)}")
            if os.path.exists(graph_path):
                found_graph = graph_path
                break
    
    if found_graph:
        try:
            photo = FSInputFile(str(found_graph))
            await callback_query.message.answer_photo(
                photo=photo,
                caption="📈 Ваши графики"
            )
        except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка при отправке фото: {e}")
    else:
        await callback_query.message.answer(
            f"⚠️ График не найден.\n\n"
            f"Искали в:\n"
            f"• {VIDEOS_DIR / 'statistics.png'}\n"
            f"• {VIDEOS_DIR / 'statistics_graph.png'}\n"
            f"• {VIDEOS_DIR / 'stats.png'}\n\n"
            f"Убедитесь, что файл графика находится в папке:\n"
            f"{VIDEOS_DIR}"
        )