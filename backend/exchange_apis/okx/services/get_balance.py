import okx.Account as Account
from config.config import settings

async def get_balance(
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
        result = client.get_account_balance()
        if result["code"] == "0":
            return result["data"][0].get("details")[2].get("availBal")
        else:
            print(f"Ошибка при получении баланса: {result['msg']}")
            return None
    except Exception as e:
        print(f"Исключение при получении баланса: {e}")
        return None