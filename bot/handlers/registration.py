from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from states.states import RegistrationStates
from aiogram.types import Message, CallbackQuery
from database.models.users.dao import UsersDAO
import keyboards.keyboards as kb
from aiogram.fsm.context import FSMContext
from config.config import settings
from utils.video_sender import send_video_instruction

router = Router()

@router.callback_query(F.data == 'register')
async def process_registration_callback(callback_query: CallbackQuery, state: FSMContext):
    
    await state.set_state(RegistrationStates.waiting_for_subscription_type)
    await callback_query.message.edit_text(
        "Пожалуйста, выберите тип подписки.", 
        reply_markup=kb.subscription_selection_keyboard
    )

@router.callback_query(F.data == "subscription_standard")
async def select_standard_subscription(callback_query: CallbackQuery, state: FSMContext):
    
    await state.update_data(subscription_type="standard")
    await state.set_state(RegistrationStates.waiting_for_exchange)
    await callback_query.message.edit_text(
        "Вы выбрали обычную подписку. Пожалуйста, выберите биржу:", 
        reply_markup=kb.exchange_selection_keyboard
    )
    await callback_query.answer()

@router.callback_query(F.data == "subscription_refferal")
async def select_referral_subscription(callback_query: CallbackQuery, state: FSMContext):
    
    await state.update_data(subscription_type="refferal")
    await state.set_state(RegistrationStates.waiting_for_exchange)

    await callback_query.message.edit_text(
        "Вы выбрали реферальную подписку. Пожалуйста, выберите биржу:",
        reply_markup=kb.exchange_selection_keyboard
    )
    await callback_query.answer()


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
    await state.set_state(RegistrationStates.waiting_for_uuid)
    await callback_query.message.delete()
    await callback_query.message.answer(
        f"Вы выбрали {exchange_name}. Пожалуйста, введите ваш uuid:"
    )
    await callback_query.answer()

@router.message(RegistrationStates.waiting_for_uuid)
async def process_uuid(message: Message, state: FSMContext, bot: Bot):
    
    await state.update_data(refferal_uuid=message.text)
    user_data = await state.get_data()
    refferal_uuid = user_data.get('refferal_uuid', message.text)
    user_exchange = user_data.get('selected_exchange')
    
    await state.set_state(RegistrationStates.waiting_for_api_key)
    
    await bot.send_message(
        chat_id=settings.MODERATOR_GROUP_ID, 
        text= "🔄 НОВЫЙ ЗАПРОС НА РЕФЕРАЛЬНУЮ ПОДПИСКУ\n\n"
            f"👤 Пользователь:\n"
            f"• ID: {message.from_user.id}\n"
            f"• Username: @{message.from_user.username or 'нет'}\n"
            f"• Имя: {message.from_user.first_name}\n"
            f"• Chat ID: {message.chat.id}\n\n"
            f"💼 Биржа: {user_exchange}\n"
            f"🔑 Реферальный UUID: <b>{refferal_uuid}</b>\n\n"
            "Пожалуйста, одобрите или отклоните запрос.",
            parse_mode="HTML",
            reply_markup=kb.get_moderation_keyboard(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                refferal_uuid=refferal_uuid
            )
        )
    
    await message.answer(
        "Спасибо! Теперь нужно дождаться подтверждения модератора.", 
    )

@router.message(RegistrationStates.waiting_for_api_key)
async def process_api_key(message: Message, state: FSMContext):
   
    await state.update_data(api_key=message.text)
    await state.set_state(RegistrationStates.waiting_for_secret_key)
    await message.answer("Пожалуйста, введите ваш Secret ключ.")

@router.message(RegistrationStates.waiting_for_secret_key)
async def process_secret_key(message: Message, state: FSMContext):
   
    await state.update_data(secret_key=message.text)
    user_data = await state.get_data()
    
    if user_data['selected_exchange'] in ['OKX', 'Bybit']:
        await state.set_state(RegistrationStates.waiting_for_passphrase)
        await message.answer("Пожалуйста, введите ваш Passphrase.")
   
    else:
        user_kwargs = {
            'user_id': message.from_user.id,
            'exchange': user_data['selected_exchange'],
            'api_key': user_data['api_key'],
            'secret_key': user_data['secret_key'],
            'subscription_end': datetime.now() + timedelta(days=365),
        }
        
        if 'refferal_uuid' in user_data:
            user_kwargs['refferal_uuid'] = user_data['refferal_uuid']
        
        if 'subscription_type' in user_data:
            user_kwargs['subscription_type'] = user_data['subscription_type']
        
        await UsersDAO.add_or_update(**user_kwargs)
        await state.clear()
        await message.answer(
            "Регистрация завершена успешно!", 
            reply_markup=kb.after_registration_keyboard
        )

@router.message(RegistrationStates.waiting_for_passphrase)
async def process_passphrase(message: Message, state: FSMContext):
    
    await state.update_data(passphrase=message.text)
    user_data = await state.get_data()
    
    user_kwargs = {
        'user_id': message.from_user.id,
        'exchange': user_data['selected_exchange'],
        'api_key': user_data['api_key'],
        'secret_key': user_data['secret_key'],
        'passphrase': user_data['passphrase'],
        'subscription_end': datetime.now() + timedelta(days=365),
    }
    
    if 'refferal_uuid' in user_data:
        user_kwargs['refferal_uuid'] = user_data['refferal_uuid']
    
    if 'subscription_type' in user_data:
        user_kwargs['subscription_type'] = user_data['subscription_type']
    
    await UsersDAO.add_or_update(**user_kwargs)
    await state.clear()
    await message.answer(
        "Регистрация завершена успешно!",
        reply_markup=kb.after_registration_keyboard
    )