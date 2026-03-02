import asyncio
import sys

sys.path.append('.')

async def test_get_symbol_info():
    """Тестирование получения информации о символе"""
    
    try:
        from backend.exchange_apis.bingx.services.get_symbol_info import get_symbol_info
        
        # Тестовые символы (популярные пары)
        test_symbols = [
            "BTC-USDT",      # Биткоин
            "ETH-USDT",      # Эфириум  
            "SOL-USDT",      # Solana
            "DOGE-USDT",     # Dogecoin
            "ADA-USDT",      # Cardano
            "XRP-USDT",      # Ripple
            "LTC-USDT",      # Litecoin
            "DOT-USDT",      # Polkadot
        ]
        
        print("🧪 Тестирование функции get_symbol_info")
        print("=" * 60)
        
        successful_tests = 0
        failed_tests = 0
        
        for symbol in test_symbols:
            print(f"\n📊 Тестируем: {symbol}")
            print("-" * 40)
            
            try:
                # Получаем информацию о символе
                symbol_info = await get_symbol_info(symbol)
                
                # Проверяем структуру ответа
                if symbol_info and isinstance(symbol_info, dict):
                    print(f"✅ Информация получена")
                    
                    # Проверяем наличие всех ожидаемых полей
                    expected_fields = ['minQty', 'stepSize', 'minUSDT']
                    missing_fields = [field for field in expected_fields if field not in symbol_info]
                    
                    if missing_fields:
                        print(f"❌ Отсутствуют поля: {missing_fields}")
                        print(f"   Полученные данные: {symbol_info}")
                        failed_tests += 1
                        continue
                    
                    # Выводим информацию
                    min_qty = symbol_info['minQty']
                    step_size = symbol_info['stepSize']
                    min_usdt = symbol_info['minUSDT']
                    
                    print(f"   • minQty (tradeMinQuantity): {min_qty}")
                    print(f"   • stepSize (quantityPrecision): {step_size}")
                    print(f"   • minUSDT (tradeMinUSDT): {min_usdt}")
                    
                    # Проверяем типы данных
                    print(f"\n   Проверка типов данных:")
                    
                    # Проверяем minQty
                    if min_qty is None:
                        print(f"   ⚠️  minQty: None")
                    else:
                        try:
                            min_qty_float = float(min_qty)
                            print(f"   ✅ minQty: число ({min_qty_float})")
                            
                            # Проверяем разумность значения
                            if min_qty_float <= 0:
                                print(f"   ⚠️  minQty не положительное: {min_qty_float}")
                            elif min_qty_float < 0.000001:
                                print(f"   ⚠️  Очень маленький minQty: {min_qty_float}")
                            elif min_qty_float > 100:
                                print(f"   ⚠️  Очень большой minQty: {min_qty_float}")
                                
                        except (ValueError, TypeError) as e:
                            print(f"   ❌ minQty не число: {min_qty} (ошибка: {e})")
                    
                    # Проверяем stepSize (quantityPrecision)
                    if step_size is None:
                        print(f"   ⚠️  stepSize: None")
                    else:
                        try:
                            # quantityPrecision обычно целое число (например, 3 для точности 0.001)
                            step_size_int = int(step_size)
                            print(f"   ✅ stepSize: целое число ({step_size_int})")
                            
                            # Преобразуем в фактический step size
                            if step_size_int >= 0:
                                actual_step = 10 ** (-step_size_int) if step_size_int > 0 else 1
                                print(f"   📐 Фактический шаг: {actual_step}")
                            else:
                                print(f"   ⚠️  Отрицательный precision: {step_size_int}")
                                
                        except (ValueError, TypeError) as e:
                            print(f"   ❌ stepSize не целое число: {step_size} (ошибка: {e})")
                    
                    # Проверяем minUSDT
                    if min_usdt is None:
                        print(f"   ⚠️  minUSDT: None")
                    else:
                        try:
                            min_usdt_float = float(min_usdt)
                            print(f"   ✅ minUSDT: число ({min_usdt_float})")
                            
                            if min_usdt_float <= 0:
                                print(f"   ⚠️  minUSDT не положительное: {min_usdt_float}")
                            elif min_usdt_float < 1:
                                print(f"   ⚠️  Маленький minUSDT: {min_usdt_float}")
                                
                        except (ValueError, TypeError) as e:
                            print(f"   ❌ minUSDT не число: {min_usdt} (ошибка: {e})")
                    
                    successful_tests += 1
                    
                else:
                    print(f"❌ Получены некорректные данные: {symbol_info}")
                    failed_tests += 1
                    
            except ValueError as e:
                if "не найдена" in str(e):
                    print(f"❌ Символ не найден: {e}")
                else:
                    print(f"❌ Ошибка получения данных: {e}")
                failed_tests += 1
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                failed_tests += 1
        
        # Итоги
        print("\n" + "=" * 60)
        print("📈 ИТОГИ ТЕСТИРОВАНИЯ:")
        print(f"✅ Успешных тестов: {successful_tests}")
        print(f"❌ Проваленных тестов: {failed_tests}")
        print(f"📊 Всего тестов: {len(test_symbols)}")
        
        if successful_tests > 0:
            print("\n🎉 Функция работает корректно!")
        else:
            print("\n😞 Требуется дополнительная отладка")
        print("=" * 60)
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверьте путь к модулю get_symbol_info")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_get_symbol_info())