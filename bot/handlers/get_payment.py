from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config.config import TARIFFS
from utils.create_check_payment import create_yoomoney_payment, check_yoomoney_payment
import keyboards.keyboards as kb 

router = Router()

@router.callback_query(F.data.startswith("tariff:"))
async def process_tariff_selection(callback_query: CallbackQuery, state: FSMContext):
    tariff_id = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id
    await callback_query.answer()

    if tariff_id not in TARIFFS:
        await callback_query.message.answer("Выбран неверный тариф. Пожалуйста, выберите снова.")
        return

    tariff = TARIFFS[tariff_id]
    await state.update_data(
        tariff_id=tariff_id,
        tariff_name=tariff["name"],
        tariff_price=tariff["price"],
        final_price=tariff["price"],
        affiliate_username = None,
        tariff_days=tariff["days"]
    )
    
    payment_info = create_yoomoney_payment(
        user_id=user_id,
        amount=tariff["price"],
        description=f"Оплата подписки {tariff['name']} для пользователя {user_id}"
    )
    if payment_info["status"] == "success":
        await callback_query.message.edit_text(
            f"Пожалуйста, перейдите по ссылке для оплаты: {payment_info['payment_url']}\n"
            "После оплаты нажмите кнопку 'Проверить оплату'.",
            reply_markup=kb.get_check_payment_keyboard(payment_info["label"])
        )
    else:
        await callback_query.message.answer("Произошла ошибка при создании платежа. Пожалуйста, попробуйте снова.")