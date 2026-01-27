from aiogram.fsm.state import StatesGroup, State

class RegistrationStates(StatesGroup):
    waiting_for_exchange = State()
    waiting_for_api_key = State()
    waiting_for_secret_key = State()
    waiting_for_passphrase = State()
    