import okx.Account as Account
from config.config import settings

async def get_open_positions(
        api_key: str,
        secret_key: str,
        passphrase: str
):
    try:
        client = Account.AccountAPI(
            api_key=api_key, 
            api_secret_key=secret_key,
            passphrase=passphrase,
            flag=settings.OKX_FLAG,
        )
        result = client.get_positions()
        if result["code"] == "0":
            return result["data"]
        else:
            print(f"Ошибка при получении баланса: {result['msg']}")
            return None
    except Exception as e:
        print(f"Исключение при получении баланса: {e}")
        return None