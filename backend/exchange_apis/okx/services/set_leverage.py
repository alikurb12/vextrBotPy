import okx.Account as Account
from config.config import settings

async def set_leverage(
        api_key : str,
        secret_key : str,
        passphrase : str,
        symbol : str,
        position_side : str,
):
    
    try:
        client = Account.AccountAPI(
            api_key=api_key,
            api_secret_key=secret_key,
            passphrase=passphrase,
            flag=settings.OKX_FLAG,
        )
        result = client.set_leverage(
            instId=symbol,
            mgnMode="isolated",
            posSide=position_side.lower(),
            lever=str(settings.LEVERAGE_LEVEL)
        )

        if result["code"] == "0":
            return result
        else:
            print(f"Ошибка при выставлении торгового плеча: {result['msg']}")
            return None
    except Exception as e:
        print(f"Исключение при выставлении торгового плеча {e}")
        return None