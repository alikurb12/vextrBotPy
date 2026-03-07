import asyncio
import sys
sys.path.append('.')

# Импортируем вашу функцию
from backend.exchange_apis.okx.services.set_tp_order import set_tp_orders # замените на правильный путь

async def test_your_function():
    print("🧪 Тестирование вашей функции set_tp_order")
    print("=" * 50)
    api_key = "4c56b9f1-11ac-481a-b8b7-2a5e43903808"
    secret_key = "04591FF46CAFB7DD0DB580A9CDFC0DFF"
    passphrase = "Alikurb!2"
    
    if not all([api_key, secret_key, passphrase]):
        print("❌ Все поля должны быть заполнены!")
        return
    
    print(f"\n🔑 API Key: {api_key[:10]}...")
    print("=" * 50)
    
    # Вызываем вашу функцию
    result = await set_tp_orders(api_key, secret_key, passphrase, "ETH-USDT-SWAP", "long", 0.1, [2100, 2200, 2300], )
    if result:
        print("✅ Функция вернула данные:")
        print(result)
    else:
        print("❌ Функция вернула None")

if __name__ == "__main__":
    asyncio.run(test_your_function())