from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
import keyboards.keyboards as kb
from states.register_states import RegistrationStates

router = Router()

@router.callback_query(F.data == 'skip_promo')
async def skip_promo_code(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(promo_code=None)
    await state.set_state(RegistrationStates.waiting_for_tariff)
    await callback_query.message.edit_text(
        "Пожалуйста, выберите тариф:",
        reply_markup=kb.get_tariff_selection_keyboard(),
    )
    

@router.message(RegistrationStates.waiting_for_promo)
async def process_promo_code(message: Message, state: FSMContext):
    await state.update_data(promo_code=message.text)
    await state.set_state(RegistrationStates.waiting_for_tariff)
    await message.edit_text(
        "Пожалуйста, выберите тариф:",
        reply_markup=kb.get_tariff_selection_keyboard(),
    )