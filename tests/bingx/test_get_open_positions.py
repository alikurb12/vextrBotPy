import asyncio
import sys
import os
import json

sys.path.append('.')

async def test_get_open_positions():
    """Тестирование получения открытых позиций"""
    
    try:
        from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions
        
        print("🧪 Тестирование функции get_open_positions")
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
            # Получаем открытые позиции
            print("Получаем открытые позиции...")
            positions_data = await get_open_positions(api_key, secret_key)
            
            if positions_data is not None:
                print("✅ Данные получены")
                
                # Проверяем тип данных
                if isinstance(positions_data, list):
                    print(f"📊 Получено позиций: {len(positions_data)}")
                    
                    # Фильтруем только активные позиции (ненулевой объем)
                    active_positions = []
                    for position in positions_data:
                        try:
                            position_amt = float(position.get("positionAmt", 0))
                            if position_amt != 0:
                                active_positions.append(position)
                        except (ValueError, TypeError):
                            continue
                    
                    print(f"📈 Активных позиций (non-zero): {len(active_positions)}")
                    
                    if active_positions:
                        print("\n📋 Детальная информация об активных позициях:")
                        print("-" * 60)
                        
                        total_unrealized_pnl = 0
                        total_position_value = 0
                        
                        for i, position in enumerate(active_positions, 1):
                            symbol = position.get("symbol", "N/A")
                            position_side = position.get("positionSide", "N/A")
                            position_amt = float(position.get("positionAmt", 0))
                            entry_price = float(position.get("entryPrice", 0))
                            mark_price = float(position.get("markPrice", 0))
                            unrealized_pnl = float(position.get("unRealizedProfit", 0))
                            liquidation_price = position.get("liquidationPrice")
                            leverage = position.get("leverage", "N/A")
                            margin_type = position.get("marginType", "N/A")
                            
                            # Рассчитываем стоимость позиции
                            position_value = abs(position_amt) * entry_price
                            total_position_value += position_value
                            total_unrealized_pnl += unrealized_pnl
                            
                            print(f"\n{i}. {symbol}")
                            print(f"   Сторона: {position_side}")
                            print(f"   Объем: {position_amt}")
                            print(f"   Цена входа: ${entry_price:,.4f}")
                            print(f"   Текущая цена: ${mark_price:,.4f}")
                            print(f"   Нереализованный PnL: ${unrealized_pnl:,.4f}")
                            
                            # Цвет для PnL
                            if unrealized_pnl > 0:
                                print(f"   📈 В плюсе: +${unrealized_pnl:,.4f}")
                            elif unrealized_pnl < 0:
                                print(f"   📉 В минусе: ${unrealized_pnl:,.4f}")
                            
                            if liquidation_price:
                                liq_price = float(liquidation_price)
                                if position_side == "LONG":
                                    distance_pct = ((mark_price - liq_price) / mark_price) * 100
                                    print(f"   ⚠️  Ликвидация: ${liq_price:,.4f} (-{distance_pct:.2f}%)")
                                else:  # SHORT
                                    distance_pct = ((liq_price - mark_price) / mark_price) * 100
                                    print(f"   ⚠️  Ликвидация: ${liq_price:,.4f} (+{distance_pct:.2f}%)")
                            
                            print(f"   Плечо: {leverage}x")
                            print(f"   Тип маржи: {margin_type}")
                            
                            # Дополнительная информация
                            if "isolatedMargin" in position:
                                isolated_margin = float(position.get("isolatedMargin", 0))
                                print(f"   Изолированная маржа: ${isolated_margin:,.4f}")
                            
                            # Рассчитываем ROI
                            if entry_price > 0:
                                if position_side == "LONG":
                                    price_change_pct = ((mark_price - entry_price) / entry_price) * 100
                                else:  # SHORT
                                    price_change_pct = ((entry_price - mark_price) / entry_price) * 100
                                
                                print(f"   📊 Изменение цены: {price_change_pct:+.2f}%")
                        
                        # Сводка
                        print("\n" + "=" * 60)
                        print("📊 СВОДКА ПО АКТИВНЫМ ПОЗИЦИЯМ:")
                        print(f"   Всего позиций: {len(active_positions)}")
                        print(f"   Общая стоимость: ${total_position_value:,.2f}")
                        print(f"   Общий PnL: ${total_unrealized_pnl:,.4f}")
                        
                        if total_unrealized_pnl > 0:
                            print(f"   🎉 Общая прибыль: +${total_unrealized_pnl:,.4f}")
                        elif total_unrealized_pnl < 0:
                            print(f"   😞 Общий убыток: ${total_unrealized_pnl:,.4f}")
                        
                        # Анализ по сторонам
                        long_positions = [p for p in active_positions if p.get("positionSide") == "LONG"]
                        short_positions = [p for p in active_positions if p.get("positionSide") == "SHORT"]
                        
                        print(f"\n   LONG позиций: {len(long_positions)}")
                        print(f"   SHORT позиций: {len(short_positions)}")
                        
                    else:
                        print("\nℹ️  Нет активных позиций (все позиции с нулевым объемом)")
                        
                        # Покажем структуру данных для понимания
                        if positions_data:
                            print("\n📋 Структура данных позиций:")
                            sample_position = positions_data[0]
                            print(f"   Доступные поля: {list(sample_position.keys())}")
                            
                            # Покажем пример позиции
                            print(f"\n   Пример позиции (первая в списке):")
                            for key, value in sample_position.items():
                                if isinstance(value, (int, float, str)):
                                    print(f"     {key}: {value}")
                
                else:
                    print(f"❌ Ожидался список, получен: {type(positions_data)}")
                    print(f"   Данные: {positions_data}")
                    
            else:
                print("❌ Получены пустые данные (None)")
                
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
        print("1. Файл get_open_positions.py существует")
        print("2. Файлы get_sign.py и parseParam.py существуют")
        print("3. Файл config.py настроен корректно")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_get_open_positions())