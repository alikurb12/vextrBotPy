import asyncio

from backend.exchange_apis.bingx.router import open_position_for_all_users

# if __name__ == "__main__":
#     asyncio.run(get_users_balances())

if __name__ == "__main__":
    asyncio.run(open_position_for_all_users(
        symbol="ADA-USDT",
        side="BUY",
        stop_loss=0.24,
        take_profit_1=0.4,
        take_profit_2=0.5,
        take_profit_3=0.6,
    ))