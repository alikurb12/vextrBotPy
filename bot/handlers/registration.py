from aiogram import Router, F
from states.states import RegistrationStates
from aiogram.types import Message, CallbackQuery
from database.models.users.dao import UsersDAO
import keyboards.keyboards as kb
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(F.data == 'register')
async def process_registration_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationStates.waiting_for_exchange)
    await callback_query.message.edit_text(
        "Пожалуйста, выберите биржу для регистрации API ключей.", 
        reply_markup=kb.exchange_selection_keyboard
)

@router.callback_query(F.data == "exchange_bitget")
async def select_binance(callback_query: CallbackQuery, state: FSMContext):
    await process_exchange_selection_from_callback(callback_query, state, "Bitget")

@router.callback_query(F.data == "exchange_bybit")
async def select_bybit(callback_query: CallbackQuery, state: FSMContext):
    await process_exchange_selection_from_callback(callback_query, state, "Bybit")

@router.callback_query(F.data == "exchange_okx")
async def select_okx(callback_query: CallbackQuery, state: FSMContext):
    await process_exchange_selection_from_callback(callback_query, state, "OKX")

@router.callback_query(F.data == "exchange_bingx")
async def select_bingx(callback_query: CallbackQuery, state: FSMContext):
    await process_exchange_selection_from_callback(callback_query, state, "BingX")

async def process_exchange_selection_from_callback(callback_query: CallbackQuery, state: FSMContext, exchange_name: str):
    await state.update_data(selected_exchange=exchange_name)
    await state.set_state(RegistrationStates.waiting_for_api_key)
    await callback_query.message.delete()
    await callback_query.message.answer(
        f"Вы выбрали {exchange_name}. Пожалуйста, введите ваш API ключ:"
    )
    await callback_query.answer()

@router.message(RegistrationStates.waiting_for_api_key)
async def process_api_key(message: Message, state: FSMContext):
    await state.update_data(api_key=message.text)
    await state.set_state(RegistrationStates.waiting_for_secret_key)
    await message.answer("Пожалуйста, введите ваш Secret ключ.")

@router.message(RegistrationStates.waiting_for_secret_key)
async def process_secret_key(message: Message, state: FSMContext):
    await state.update_data(secret_key=message.text)
    user_data = await state.get_data()
    if user_data['selected_exchange'] == 'OKX' or user_data['selected_exchange'] == 'Bybit':
        await state.set_state(RegistrationStates.waiting_for_passphrase)
        await message.answer("Пожалуйста, введите ваш Passphrase.")
    else:
        await UsersDAO.add_or_update(
            user_id=message.from_user.id,
            exchange=user_data['selected_exchange'],
            api_key=user_data['api_key'],
            secret_key=user_data['secret_key']
        )
    
        await state.clear()
        await message.answer("Регистрация завершена успешно!", reply_markup=kb.start_keyboard)

@router.message(RegistrationStates.waiting_for_passphrase)
async def process_passphrase(message: Message, state: FSMContext):
    await state.update_data(passphrase=message.text)
    user_data = await state.get_data()
    await UsersDAO.add_or_update(
        user_id=message.from_user.id,
        exchange=user_data['selected_exchange'],
        api_key=user_data['api_key'],
        secret_key=user_data['secret_key'],
        passphrase=user_data['passphrase']
    )
    await state.clear()
    await message.answer("Регистрация завершена успешно!", reply_markup=kb.start_keyboard)