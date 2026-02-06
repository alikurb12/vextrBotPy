import time
from backend.exchange_apis.bingx.services.get_server_time import get_server_time
TIME_OFFSET = 0

async def parseParam(paramsMap: dict) -> str:
    global TIME_OFFSET
    if not hasattr(parseParam, "TIME_OFFSET"):
        parseParam.TIME_OFFSET = await get_server_time()
        TIME_OFFSET = parseParam.TIME_OFFSET
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    timestamp = int(time.time() * 1000) + TIME_OFFSET
    return paramsStr + "&timestamp=" + str(timestamp) if paramsStr else "timestamp=" + str(timestamp) 