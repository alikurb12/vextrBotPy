from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Зарегестрировать API", callback_data="register"), 
            InlineKeyboardButton(text="Сбросить API", callback_data="reset_api"),
        ],
    ],
)

reset_api_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Регистрация", callback_data="register")]
    ],
)

exchange_selection_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="BingX", callback_data="exchange_bingx"), 
            InlineKeyboardButton(text="OKX", callback_data="exchange_okx"),
        ],
        [
            InlineKeyboardButton(text="Bybit", callback_data="exchange_bybit"),
            InlineKeyboardButton(text="Bitget", callback_data="exchange_bingx"),    
        ],   
        
    ],
)

subscription_selection_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Обычная подписка", callback_data="subscription_standard")],
        [InlineKeyboardButton(text="Реферальная подписка", callback_data="subscription_refferal")],
    ]
)

def get_moderation_keyboard(user_id: int, chat_id: int, refferal_uuid: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять", 
                    callback_data=f"approve:{user_id}:{chat_id}:{refferal_uuid}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить", 
                    callback_data=f"reject:{user_id}:{chat_id}:{refferal_uuid}"
                )
            ]
        ]
    )