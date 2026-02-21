from fastapi import FastAPI
from backend.exchange_apis.bingx.router import open_position_for_all_users, move_sl_to_breakeven_for_all_users
from backend.utils.signal_shema import SignalSchema
from backend.utils.send_notification import notify_users_position_opened, notify_users_sl_moved_to_breakeven

app = FastAPI()

@app.post("/webhook")
async def webhook(data: SignalSchema):
    
    if data.action == "BUY" or data.action == "SELL":
        await open_position_for_all_users(
            symbol=data.symbol,
            side=data.action,
            stop_loss=data.stop_loss,
            take_profit_1=data.take_profit_1,
            take_profit_2=data.take_profit_2,
            take_profit_3=data.take_profit_3,
        )
        await notify_users_position_opened(
            symbol=data.symbol,
            side=data.action,
            entry_price=data.price,
            stop_loss=data.stop_loss,
            take_profit_1=data.take_profit_1,
            take_profit_2=data.take_profit_2,
            take_profit_3=data.take_profit_3,
        )
    
    elif data.action == "MOVE_SL":
        await notify_users_sl_moved_to_breakeven(symbol=data.symbol)
        await move_sl_to_breakeven_for_all_users(symbol=data.symbol)
    
    return {"message": "Webhook received successfully"}