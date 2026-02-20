import asyncio

from backend.exchange_apis.bingx.router import open_position_for_all_users, move_sl_to_breakeven_for_all_users

# if __name__ == "__main__":
#     asyncio.run(get_users_balances())

if __name__ == "__main__":
    asyncio.run(open_position_for_all_users(
        symbol="XRP-USDT",
        side="BUY",
        stop_loss=1.3,
        take_profit_1=1.5,
        take_profit_2=1.6,
        take_profit_3=1.7,
    ))


# if __name__ == "__main__":
#     asyncio.run(open_position_for_all_users(
#         symbol="XRP-USDT",
#         side="SELL",
#         stop_loss=1.5,
#         take_profit_1=1.3,
#         take_profit_2=1.2,
#         take_profit_3=1.1,
#     ))


# if __name__ == "__main__":
#     asyncio.run(move_sl_to_breakeven_for_all_users(
#         symbol="XRP-USDT",
#     ))