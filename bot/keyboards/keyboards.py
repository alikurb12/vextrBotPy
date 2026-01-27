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

exchange_selection_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="BingX")],
        [KeyboardButton(text="OKX")],
        [KeyboardButton(text="Bybit")],
        [KeyboardButton(text="Bitget")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите биржу",
)