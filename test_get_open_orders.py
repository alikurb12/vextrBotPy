import asyncio
import sys
import os
import json

sys.path.append('.')

async def test_get_open_orders():
    """Тестирование получения открытых ордеров"""
    
    try:
        from backend.exchange_apis.bingx.services.get_open_orders import get_open_orders
        
        print("🧪 Тестирование функции get_open_orders")
        print("=" * 60)
        
        # Запросим API ключи у пользователя
        api_key = input("Введите API ключ BingX: ").strip()
        secret_key = input("Введите Secret ключ BingX: ").strip()
        
        if not api_key or not secret_key:
            print("❌ API ключи не указаны")
            return
        
        print(f"\n🔑 Тестирование с API ключом: {api_key[:10]}...")
        print("-" * 40)
        
        try:
            # Получаем открытые ордера
            print("Получаем открытые ордера...")
            orders_data = await get_open_orders(api_key, secret_key)
            
            if orders_data:
                print("✅ Данные получены")
                
                # Проверяем структуру ответа
                if isinstance(orders_data, dict):
                    print(f"\n📊 Структура данных:")
                    for key, value in orders_data.items():
                        if isinstance(value, list):
                            print(f"  • {key}: список из {len(value)} элементов")
                        else:
                            print(f"  • {key}: {type(value).__name__}")
                
                # Проверяем наличие ордеров
                orders = orders_data.get('orders', [])
                print(f"\n📈 Открытых ордеров: {len(orders)}")
                
                if orders:
                    print("\n📋 Список открытых ордеров:")
                    print("-" * 50)
                    
                    for i, order in enumerate(orders, 1):
                        print(f"\n{i}. {order.get('symbol', 'N/A')}:")
                        print(f"   ID: {order.get('orderId', 'N/A')}")
                        print(f"   Тип: {order.get('type', 'N/A')}")
                        print(f"   Сторона: {order.get('side', 'N/A')}")
                        print(f"   Позиция: {order.get('positionSide', 'N/A')}")
                        print(f"   Количество: {order.get('quantity', 'N/A')}")
                        print(f"   Цена: {order.get('price', 'N/A')}")
                        
                        # Проверяем TP/SL ордера
                        if order.get('type') in ['STOP_MARKET', 'TAKE_PROFIT_MARKET']:
                            print(f"   Стоп-цена: {order.get('stopPrice', 'N/A')}")
                            if order.get('type') == 'STOP_MARKET':
                                print(f"   ⚠️  Это стоп-лосс ордер")
                            else:
                                print(f"   ✅ Это тейк-профит ордер")
                        
                        # Статус ордера
                        status = order.get('status', 'N/A')
                        status_icon = "✅" if status == 'NEW' else "⚠️"
                        print(f"   Статус: {status_icon} {status}")
                        
                else:
                    print("ℹ️  Нет открытых ордеров")
                    
            else:
                print("❌ Получены пустые данные")
                
        except ValueError as e:
            print(f"❌ Ошибка API: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("✅ Тест завершен")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверьте пути импорта:")
        print("1. Файл get_open_orders.py существует")
        print("2. Файлы get_sign.py и parseParam.py существуют")
        print("3. Файл config.py настроен корректно")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_get_open_orders())