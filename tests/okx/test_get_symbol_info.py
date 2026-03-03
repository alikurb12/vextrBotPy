import asyncio
import sys
sys.path.append('.')

# Импортируем вашу функцию
from backend.exchange_apis.okx.services.get_symbol_info import get_symbol_info# замените на правильный путь

async def test_your_function():
    print("🧪 Тестирование вашей функции get_symbol_info")
    print("=" * 50)
    # Вызываем вашу функцию
    result = await get_symbol_info("ETH-USDT-SWAP")
    if result:
        print("✅ Функция вернула данные:")
        print(result)
    else:
        print("❌ Функция вернула None")

if __name__ == "__main__":
    asyncio.run(test_your_function())