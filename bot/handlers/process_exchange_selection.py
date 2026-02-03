from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
import keyboards.keyboards as kb
from states.register_states import RegistrationStates
from utils.video_sender import send_video_instruction

router = Router()

@router.callback_query(F.data == "exchange_bitget")
async def select_binance(callback_query: CallbackQuery, state: FSMContext):
    
    await send_video_instruction(
        callback_query, 
        "bitget.mp4", 
        "Инструкция по получению API ключей для Bitget."
    )
    await process_exchange_selection_from_callback(callback_query, state, "Bitget")

@router.callback_query(F.data == "exchange_bybit")
async def select_bybit(callback_query: CallbackQuery, state: FSMContext):
    
    await send_video_instruction(
        callback_query, 
        "bybit.mp4", 
        "Инструкция по получению API ключей для Bybit."
    )
    await process_exchange_selection_from_callback(callback_query, state, "Bybit")

@router.callback_query(F.data == "exchange_okx")
async def select_okx(callback_query: CallbackQuery, state: FSMContext):
    
    await send_video_instruction(
        callback_query, 
        "okx.mp4", 
        "Инструкция по получению API ключей для OKX."
    )
    await process_exchange_selection_from_callback(callback_query, state, "OKX")

@router.callback_query(F.data == "exchange_bingx")
async def select_bingx(callback_query: CallbackQuery, state: FSMContext):
    
    await send_video_instruction(
        callback_query, 
        "bingx.mp4", 
        "Инструкция по получению API ключей для BingX."
    )
    await process_exchange_selection_from_callback(callback_query, state, "BingX")

async def process_exchange_selection_from_callback(callback_query: CallbackQuery, state: FSMContext, exchange_name: str):
    await state.update_data(selected_exchange=exchange_name)
    user_data = await state.get_data()
    
    subscription_type = user_data.get('subscription_type')
    
    if subscription_type == "refferal":
        await state.set_state(RegistrationStates.waiting_for_uuid)
        await callback_query.message.delete()
        await callback_query.message.answer(
            f"Вы выбрали {exchange_name}. Пожалуйста, введите ваш UUID для реферальной подписки:"
        )
    else:
        await state.set_state(RegistrationStates.waiting_for_api_key)
        await callback_query.message.delete()
        await callback_query.message.answer(
            f"Вы выбрали {exchange_name}. Пожалуйста, введите ваш API ключ:"
        )
    
    await callback_query.answer()
