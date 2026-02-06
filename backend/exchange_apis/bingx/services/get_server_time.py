from config.config import settings
import httpx
import time

async def get_server_time() -> int:
    try:
        url = f"{settings.BINGX_API_URL}/openApi/swap/v2/server/time"
        responce = httpx.get(url)
        data = responce.json()
        if "code" in data and data["code"] == 0:
            server_time = int(data['data']['serverTime'])
            local_time = int(time.time() * 1000)
            offset = server_time - local_time
            return offset
        else:
            raise ValueError("Ошибка получения времени сервера")
    except Exception as e:
        print(f"Ошибка в получении времени {e}")
        return 0