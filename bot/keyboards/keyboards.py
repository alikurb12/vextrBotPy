from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.config import TARIFFS, settings

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

after_registration_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Главное меню", callback_data="main_menu"),
        ]
    ],
)

def get_main_menu_kb(is_active: bool = True):
    pause_text = "▶️ Возобновить торговлю" if not is_active else "⏸ Пауза торговли"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 Мой статус", callback_data="my_status"),
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="statistics"),
            ],
            [
                InlineKeyboardButton(text="📋 Открытые позиции", callback_data="get_my_positions"),
            ],
            [
                InlineKeyboardButton(text=pause_text, callback_data="toggle_trading"),
            ],
            [
                InlineKeyboardButton(text="🔑 Сбросить API ключи", callback_data="reset_api"),
            ],
        ],
    )

# Оставляем старую для обратной совместимости
main_menu_keyboard = get_main_menu_kb()

my_status_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙", callback_data="main_menu"),
            InlineKeyboardButton(text="🔑 Сбросить API ключи", callback_data="reset_api"),
        ]
    ],
)

statistics_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        ]
    ],
)

def get_tariff_selection_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for tariff_id, tariff in TARIFFS.items():
        kb.inline_keyboard.append([InlineKeyboardButton(
            text=f"{tariff['name']} – {tariff['price']}₽",
            callback_data=f"tariff:{tariff_id}"
        )])
    kb.inline_keyboard.append([InlineKeyboardButton(text="Поддержка", url=f"https://t.me/{settings.SUPPORT_CONTACT.lstrip('@')}")])
    return kb

promo_code_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Пропустить", callback_data="skip_promo"),
        ]
    ],
)

def get_check_payment_keyboard(label: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Проверить оплату", 
                    callback_data=f"check_payment:{label}"
                )
            ]
        ]
    )

my_status_kb_after_signal = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Главное меню", callback_data="main_menu_after_signal"),
        ],
    ]
)
