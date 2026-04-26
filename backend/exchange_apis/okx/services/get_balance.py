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
            details = result["data"][0].get("details", [])
            # Ищем USDT по имени, не по индексу
            for item in details:
                if item.get("ccy") == "USDT":
                    balance = item.get("availBal")
                    print(f"OKX USDT баланс: {balance}")
                    return balance
            print(f"USDT не найден в details: {details}")
            return None
        else:
            print(f"Ошибка при получении баланса: {result['msg']}")
            return None
    except Exception as e:
        print(f"Исключение при получении баланса: {e}")
        return None
