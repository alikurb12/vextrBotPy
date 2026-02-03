from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
import keyboards.keyboards as kb
from states.register_states import RegistrationStates

router = Router()


@router.message(RegistrationStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(RegistrationStates.waiting_for_promo)
    await message.answer(
        "Если у вас есть промокод, введите его сейчас. "
        "Если нет, то нажмите на кнопку <b>'Пропустить'</b> ниже.",
        reply_markup=kb.promo_code_keyboard,
        parse_mode="HTML",
    )