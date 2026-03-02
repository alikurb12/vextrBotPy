import okx.Trade as Trade

async def close_position(
        api_key : str,
        secret_key : str,
        passphrase : str,
        symbol : str,
        position_syde : str,
):
    try:
        trade = Trade.TradeAPI(
            api_key=api_key,
            api_secret_key=secret_key,
            passphrase=passphrase,
        )
        result = trade.close_positions(
            instId=symbol,
            posSide=position_syde,
            mgnMode="isolated",
        )
        if result["code"] == "0":
            return result
        else:
            print(f"Ошибка при закрытии сделки: {result['msg']}")
            return None
    except Exception as e:
        print(f"Исключение при закрытии сделки: {e}")
        return None