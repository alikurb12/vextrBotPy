from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from utils.create_check_payment import check_yoomoney_payment
import keyboards.keyboards as kb 
from database.models.payments.dao import PaymentsDAO

router = Router()

@router.callback_query(F.data.startswith("check_payment:"))
async def process_check_payment(callback_query: CallbackQuery, state: FSMContext):
    label = callback_query.data.split(":")[1]
    
    await callback_query.answer()

    payment_successful = check_yoomoney_payment(label)

    if payment_successful:
        user_data = await state.get_data()
        await state.update_data(label=label)
        tariff_name = user_data.get("tariff_name", "Неизвестный тариф")
        await callback_query.message.edit_text(
            f"Оплата успешно подтверждена! Вы приобрели подписку: {tariff_name}."
            f"Выберите биржу для продолжения регистрации.",
            reply_markup=kb.exchange_selection_keyboard
        )

    else:
        await callback_query.message.edit_text(
            "Оплата не найдена или не подтверждена. Пожалуйста, убедитесь, что вы завершили оплату, "
            "и попробуйте снова.",
            reply_markup=kb.get_check_payment_keyboard(label)
        )