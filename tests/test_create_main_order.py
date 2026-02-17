import asyncio
import sys
import os

sys.path.append('.')

async def test_create_main_order_fixed():
    """Исправленный тест создания ордера"""
    
    try:
        from backend.exchange_apis.bingx.services.create_main_order import create_main_order
        from backend.exchange_apis.bingx.services.get_current_price import get_current_price
        from backend.exchange_apis.bingx.services.get_symbol_info import get_symbol_info
        
        print("🧪 Исправленный тест create_main_order")
        print("=" * 60)
        print("⚠️  ВНИМАНИЕ: Этот тест создаст реальную сделку!")
        print("=" * 60)
        
        # Ключи
        api_key = input("API ключ BingX: ").strip()
        secret_key = input("Secret ключ BingX: ").strip()
        
        if not api_key or not secret_key:
            print("❌ API ключи не указаны")
            return
        
        print(f"\n🔑 Тестирование с API ключом: {api_key[:10]}...")
        print("-" * 40)
        
        # Параметры теста
        symbol = "BTC-USDT"
        side = "BUY"
        
        print(f"\n📊 Тестовые параметры:")
        print(f"  Символ: {symbol}")
        print(f"  Сторона: {side}")
        
        try:
            # Получаем информацию о символе
            print(f"\n🔍 Получаем информацию о {symbol}...")
            symbol_info = await get_symbol_info(symbol)
            
            print(f"  Сырые данные: {symbol_info}")
            
            min_qty = float(symbol_info.get('minQty', 0.001))
            step_size = float(symbol_info.get('stepSize', 0.001))
            quantity_precision = symbol_info.get('quantityPrecision', 3)
            
            print(f"  Минимальное количество: {min_qty}")
            print(f"  Шаг объема: {step_size}")
            print(f"  Точность количества: {quantity_precision}")
            
            # Получаем текущую цену
            current_price = await get_current_price(symbol)
            print(f"  Текущая цена: ${current_price:,.4f}")

            take_profit = current_price * 1.1
            
            # Рассчитываем тестовое количество
            # Минимум 10 USDT или минимальное количество
            min_usdt_amount = 10
            test_quantity = max(min_qty, min_usdt_amount / current_price)
            
            print(f"  Рассчитанное количество: {test_quantity}")
            
            # Округляем до шага
            if step_size > 0:
                test_quantity = round(test_quantity / step_size) * step_size
                print(f"  Округленное количество: {test_quantity}")
            else:
                # Если step_size 0 или отрицательный, используем минимальное количество
                test_quantity = min_qty
                print(f"  Используем минимальное количество: {test_quantity}")
            
            # Форматируем количество с правильной точностью
            test_quantity_str = format(test_quantity, f'.{quantity_precision}f')
            test_quantity = float(test_quantity_str)
            
            print(f"\n📈 Финальные параметры:")
            print(f"  Количество: {test_quantity}")
            print(f"  Примерная стоимость: ${test_quantity * current_price:,.2f}")
            
            # Проверяем, что количество больше 0
            if test_quantity <= 0:
                print(f"❌ Количество должно быть больше 0")
                return
            
            # Подтверждение
            confirm = input(f"\nСоздать {side} ордер на {test_quantity} {symbol}? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("❌ Тест отменен пользователем")
                return
            
            # Создаем ордер
            print(f"\n🔄 Создаем ордер...")
            try:
                order_result = await create_main_order(
                    symbol=symbol,
                    api_key=api_key,
                    secret_key=secret_key,
                    side=side,
                    quantity=test_quantity

                )
                
                if order_result:
                    print("✅ Ордер успешно создан!")
                    print(f"  Результат: {order_result}")
                    
                    # Показываем информацию об ордере
                    order_info = order_result.get("order", {})
                    if order_info:
                        print(f"\n📋 Информация об ордере:")
                        for key, value in order_info.items():
                            print(f"  {key}: {value}")
                else:
                    print("❌ Нет данных в ответе")
                    
            except ValueError as e:
                print(f"❌ Ошибка создания ордера: {e}")
                
                # Анализ ошибки
                error_msg = str(e)
                if "Invalid parameters" in error_msg:
                    print(f"\n⚠️  Возможные причины:")
                    print("  1. Неправильные параметры запроса")
                    print("  2. Отсутствует обязательный параметр 'type'")
                    print("  3. Неправильный формат количества")
                    print("  4. Проблема с символами в параметрах")
                    
                    # Выводим параметры для отладки
                    print(f"\n🔧 Для отладки создайте тестовый запрос:")
                    print(f"  symbol: {symbol}")
                    print(f"  side: {side}")
                    print(f"  positionSide: {'LONG' if side == 'BUY' else 'SHORT'}")
                    print(f"  type: MARKET")
                    print(f"  quantity: {test_quantity} (как строка: '{str(test_quantity)}')")
                    
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"❌ Ошибка получения информации: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("✅ Тест завершен")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create_main_order_fixed())