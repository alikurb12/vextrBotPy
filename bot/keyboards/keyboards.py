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