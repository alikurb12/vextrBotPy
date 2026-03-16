from pydantic import BaseModel
from typing import Optional

class SignalSchema(BaseModel):
    action : str
    symbol : str
    price : float
    stop_loss : float
    take_profit_1 : Optional[float] = None
    take_profit_2 : Optional[float] = None
    take_profit_3 : Optional[float] = None