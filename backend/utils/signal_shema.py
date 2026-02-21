from pydantic import BaseModel

class SignalSchema(BaseModel):
    action : str
    symbol : str
    stop_loss : float
    take_profit_1 : float
    take_profit_2 : float
    take_profit_3 : float