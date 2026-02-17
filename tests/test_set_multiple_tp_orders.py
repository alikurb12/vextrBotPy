#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
БЫСТРЫЙ ТЕСТ ДЛЯ УСТАНОВКИ МНОЖЕСТВЕННЫХ ТЕЙК-ПРОФИТОВ
Запуск: python quick_multiple_tp_test.py
"""

import asyncio
import sys
import os
sys.path.append('.')

async def quick_multiple_tp_test():
    """Быстрый тест установки нескольких тейк-профитов"""
    
    print("=" * 70)
    print("🚀 БЫСТРЫЙ ТЕСТ УСТАНОВКИ МНОЖЕСТВЕННЫХ ТЕЙК-ПРОФИТОВ")
    print("=" * 70)
    print("⚠️  Эта функция автоматически уменьшит количество TP при ошибке маржи")
    print("=" * 70)
    
    try:
        from backend.exchange_apis.bingx.services.set_tp_orders import set_tp_orders
        from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions
        from backend.exchange_apis.bingx.services.get_open_orders import get_open_orders
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("\n🔍 Проверьте:")
        print("   1. Файл set_tp_orders.py существует в backend/exchange_apis/bingx/services/")
        print("   2. Файл get_open_positions.py существует")
        print("   3. Файл get_open_orders.py существует")
        return
    
    # Ввод ключей
    api_key = input("\n🔑 API ключ: ").strip()
    secret_key = input("🔑 Secret ключ: ").strip()
    
    if not api_key or not secret_key:
        print("❌ Ключи не указаны")
        return
    
    # Получаем позиции
    print("\n📊 Получаем открытые позиции...")
    try:
        positions = await get_open_positions(api_key, secret_key)
    except Exception as e:
        print(f"❌ Ошибка получения позиций: {e}")
        return
    
    # Показываем активные позиции
    active = []
    for pos in positions:
        if float(pos.get("positionAmt", 0)) != 0:
            active.append(pos)
    
    if not active:
        print("❌ Нет активных позиций")
        return
    
    print(f"\n📋 АКТИВНЫЕ ПОЗИЦИИ:")
    for i, pos in enumerate(active, 1):
        symbol = pos.get("symbol")
        side = pos.get("positionSide")
        amt = abs(float(pos.get("positionAmt", 0)))
        entry = float(pos.get("entryPrice", 0)) or float(pos.get("avgPrice", 0))
        mark = float(pos.get("markPrice", 0))
        
        if side == "LONG" and entry > 0:
            profit_pct = ((mark - entry) / entry) * 100
        elif side == "SHORT" and entry > 0:
            profit_pct = ((entry - mark) / entry) * 100
        else:
            profit_pct = 0
            
        print(f"{i}. {symbol} {side}: {amt} @ ${entry:.4f} | Текущая: ${mark:.4f} ({profit_pct:+.2f}%)")
    
    # Выбор позиции
    choice = input("\n🎯 Выберите номер позиции: ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(active):
            pos = active[idx]
            symbol = pos.get("symbol")
            side = pos.get("positionSide")
            quantity = abs(float(pos.get("positionAmt", 0)))
            entry = float(pos.get("entryPrice", 0)) or float(pos.get("avgPrice", 0))
            mark = float(pos.get("markPrice", 0))
            
            # Определяем сторону для TP
            tp_side = "SELL" if side == "LONG" else "BUY"
            
            print(f"\n📊 ПОЗИЦИЯ: {symbol} {side}")
            print(f"   Количество: {quantity}")
            print(f"   Цена входа: ${entry:.4f}")
            print(f"   Текущая цена: ${mark:.4f}")
            print(f"   TP сторона: {tp_side}")
            
            # Рассчитываем рекомендуемые цены
            if side == "LONG":
                tp1 = round(entry * 1.02, 4)   # +2%
                tp2 = round(entry * 1.03, 4)   # +3%
                tp3 = round(entry * 1.05, 4)   # +5%
                tp4 = round(entry * 1.07, 4)   # +7%
                tp5 = round(entry * 1.10, 4)   # +10%
            else:  # SHORT
                tp1 = round(entry * 0.98, 4)   # -2%
                tp2 = round(entry * 0.97, 4)   # -3%
                tp3 = round(entry * 0.95, 4)   # -5%
                tp4 = round(entry * 0.93, 4)   # -7%
                tp5 = round(entry * 0.90, 4)   # -10%
            
            print(f"\n💡 РЕКОМЕНДУЕМЫЕ ЦЕНЫ:")
            print(f"   TP1 (+2%):  ${tp1:.4f}")
            print(f"   TP2 (+3%):  ${tp2:.4f}")
            print(f"   TP3 (+5%):  ${tp3:.4f}")
            print(f"   TP4 (+7%):  ${tp4:.4f}")
            print(f"   TP5 (+10%): ${tp5:.4f}")
            
            # Ввод цен TP
            print("\n📝 Введите цены тейк-профита (можно несколько через пробел)")
            tp_input = input("💰 Цены TP: ").strip()
            tp_prices = [float(x) for x in tp_input.split()]
            
            if not tp_prices:
                print("❌ Не введено ни одной цены")
                return
            
            print(f"\n📋 БУДЕТ ПРЕДПРИНЯТА ПОПЫТКА УСТАНОВИТЬ {len(tp_prices)} TP ОРДЕРОВ")
            print(f"   Цены: {tp_prices}")
            
            # Проверка цен
            invalid_prices = []
            for price in tp_prices:
                if side == "LONG" and price <= mark:
                    invalid_prices.append((price, "ниже текущей"))
                elif side == "SHORT" and price >= mark:
                    invalid_prices.append((price, "выше текущей"))
            
            if invalid_prices:
                print(f"\n⚠️  ВНИМАНИЕ: Некоторые цены {'ниже' if side=='LONG' else 'выше'} текущей:")
                for price, reason in invalid_prices:
                    print(f"   • ${price:.4f} - {reason}")
                
                confirm = input("\n   Продолжить все равно? (да/нет): ").strip().lower()
                if confirm != 'да':
                    print("❌ Тест отменен")
                    return
            
            # Показываем ожидаемое распределение
            print(f"\n📊 ОЖИДАЕМОЕ РАСПРЕДЕЛЕНИЕ:")
            
            # Рассчитываем количества (функция _split_quantity внутри set_tp_orders сделает это автоматически)
            if len(tp_prices) == 1:
                print(f"   • 1 TP: {quantity} XRP")
            elif len(tp_prices) == 2:
                qty1 = round(quantity / 2, 4)
                qty2 = round(quantity - qty1, 4)
                print(f"   • TP1: {qty1} XRP @ ${tp_prices[0]:.4f}")
                print(f"   • TP2: {qty2} XRP @ ${tp_prices[1]:.4f}")
            elif len(tp_prices) >= 3:
                qty1 = round(quantity * 0.33, 4)
                qty2 = round(quantity * 0.33, 4)
                qty3 = round(quantity - qty1 - qty2, 4)
                print(f"   • TP1: {qty1} XRP @ ${tp_prices[0]:.4f}")
                print(f"   • TP2: {qty2} XRP @ ${tp_prices[1]:.4f}")
                print(f"   • TP3: {qty3} XRP @ ${tp_prices[2]:.4f}")
                if len(tp_prices) > 3:
                    print(f"   • (остальные цены будут игнорироваться, макс. 3 TP)")
            
            # Подтверждение
            confirm = input("\n⚠️  УСТАНОВИТЬ ТЕЙК-ПРОФИТЫ? (да/нет): ").strip().lower()
            
            if confirm == 'да':
                try:
                    print(f"\n🔄 Отправка запроса с {len(tp_prices[:3])} TP ордерами...")
                    
                    result = await set_tp_orders(
                        api_key=api_key,
                        secret_key=secret_key,
                        symbol=symbol,
                        side=tp_side,
                        quantity=quantity,
                        tp_prices=tp_prices  # Передаем список цен
                    )
                    
                    print(f"\n✅ ТЕЙК-ПРОФИТЫ УСТАНОВЛЕНЫ!")
                    
                    if isinstance(result, list):
                        print(f"📦 СОЗДАНО ОРДЕРОВ: {len(result)}")
                        
                        for i, order_result in enumerate(result, 1):
                            if isinstance(order_result, dict) and 'order' in order_result:
                                order = order_result['order']
                                print(f"\n   Ордер {i}:")
                                print(f"      • ID: {order.get('orderId')}")
                                print(f"      • Цена: ${float(order.get('stopPrice', 0)):.4f}")
                                print(f"      • Количество: {order.get('quantity')}")
                            else:
                                print(f"\n   Ордер {i}: {order_result}")
                    else:
                        print(f"📦 Результат: {result}")
                    
                    # Проверяем созданные ордера
                    print("\n🔍 Проверяем созданные ордера...")
                    await asyncio.sleep(2)
                    
                    orders_data = await get_open_orders(api_key, secret_key)
                    
                    if orders_data:
                        orders = orders_data.get('orders', [])
                        tp_orders = [o for o in orders if o.get('type') == 'TAKE_PROFIT_MARKET' and o.get('symbol') == symbol]
                        
                        if tp_orders:
                            print(f"\n✅ НАЙДЕНО TP ОРДЕРОВ: {len(tp_orders)}")
                            for i, order in enumerate(tp_orders, 1):
                                print(f"\n   {i}. {order.get('symbol')} {order.get('positionSide')}:")
                                print(f"      • ID: {order.get('orderId')}")
                                print(f"      • Цена: ${float(order.get('stopPrice', 0)):.4f}")
                                print(f"      • Количество: {order.get('quantity')}")
                                print(f"      • Статус: {order.get('status')}")
                        else:
                            print(f"\n⚠️ TP ордера не найдены в списке открытых ордеров")
                    
                except ValueError as e:
                    print(f"\n❌ ОШИБКА: {e}")
                    
                    # Анализ ошибки
                    error_str = str(e).lower()
                    
                    # Проверяем коды ошибок маржи
                    margin_codes = ['80012', '80013', '80014', '101400', '101401']
                    if any(code in str(e) for code in margin_codes) or 'margin' in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Обнаружена ошибка недостаточной маржи")
                        print("   • Функция должна была автоматически переключиться на 1 TP")
                        print("   • Проверьте открытые ордера через несколько секунд")
                        
                        # Проверяем, не создался ли 1 TP автоматически
                        print("\n⏳ Ожидаем 3 секунды...")
                        await asyncio.sleep(3)
                        
                        orders_after = await get_open_orders(api_key, secret_key)
                        if orders_after:
                            tp_after = [o for o in orders_after.get('orders', []) 
                                      if o.get('type') == 'TAKE_PROFIT_MARKET' and o.get('symbol') == symbol]
                            if tp_after:
                                print(f"✅ Сработал fallback: создан 1 TP ордер")
                                for o in tp_after:
                                    print(f"   • Цена: ${float(o.get('stopPrice', 0)):.4f}")
                                    print(f"   • Количество: {o.get('quantity')}")
                            else:
                                print("❌ Fallback не сработал - ордеров нет")
                    elif "position not exist" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Убедитесь, что у вас есть открытая позиция")
                        print("   • Проверьте правильность symbol и side")
                        print(f"   • symbol: {symbol}, side: {side}, tp_side: {tp_side}")
                    elif "quantity" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Проблема с количеством")
                        print("   • Убедитесь, что quantity > 0")
                        print(f"   • quantity: {quantity}")
                    elif "price" in error_str or "stopPrice" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Проблема с ценой")
                        print(f"   • Для {side} позиции цена должна быть {'выше' if side == 'LONG' else 'ниже'} текущей")
                        print(f"   • Текущая цена: ${mark:.4f}")
                        print(f"   • Введенные цены: {tp_prices}")
                
                except Exception as e:
                    print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ Тест отменен")
        else:
            print("❌ Неверный номер позиции")
            
    except ValueError as e:
        print(f"❌ Ошибка ввода: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠️ Тест прерван пользователем")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

async def check_tp_orders_after_test():
    """Проверяет созданные TP ордера после теста"""
    try:
        from backend.exchange_apis.bingx.services.get_open_orders import get_open_orders
        
        print("\n" + "=" * 70)
        print("🔍 ПРОВЕРКА АКТИВНЫХ ТЕЙК-ПРОФИТ ОРДЕРОВ")
        print("=" * 70)
        
        api_key = input("\n🔑 API ключ (Enter для пропуска): ").strip()
        if not api_key:
            return
            
        secret_key = input("🔑 Secret ключ: ").strip()
        if not secret_key:
            return
        
        print("\n📊 Получаем открытые ордера...")
        orders_data = await get_open_orders(api_key, secret_key)
        
        if orders_data:
            orders = orders_data.get('orders', [])
            tp_orders = [o for o in orders if o.get('type') == 'TAKE_PROFIT_MARKET']
            
            if tp_orders:
                print(f"\n📋 НАЙДЕНО ТЕЙК-ПРОФИТ ОРДЕРОВ: {len(tp_orders)}")
                
                # Группируем по символам
                by_symbol = {}
                for order in tp_orders:
                    symbol = order.get('symbol')
                    if symbol not in by_symbol:
                        by_symbol[symbol] = []
                    by_symbol[symbol].append(order)
                
                for symbol, orders_list in by_symbol.items():
                    print(f"\n   {symbol}: {len(orders_list)} ордеров")
                    for i, order in enumerate(orders_list, 1):
                        print(f"      {i}. Цена: ${float(order.get('stopPrice', 0)):.4f}")
                        print(f"         Количество: {order.get('quantity')}")
                        print(f"         ID: {order.get('orderId')}")
                        print(f"         Статус: {order.get('status')}")
            else:
                print("\n✅ Нет активных тейк-профит ордеров")
        else:
            print("❌ Не удалось получить данные об ордерах")
            
    except Exception as e:
        print(f"⚠️ Ошибка проверки: {e}")

async def test_simple_case():
    """Простой тест с 3 TP для быстрой проверки"""
    
    print("\n" + "=" * 70)
    print("🧪 ПРОСТОЙ ТЕСТ С 3 TP (ДЛЯ БЫСТРОЙ ПРОВЕРКИ)")
    print("=" * 70)
    
    try:
        from backend.exchange_apis.bingx.services.set_tp_orders import set_tp_orders
        from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions
        
        api_key = input("\n🔑 API ключ: ").strip()
        secret_key = input("🔑 Secret ключ: ").strip()
        
        positions = await get_open_positions(api_key, secret_key)
        
        # Ищем XRP-USDT
        target = None
        for pos in positions:
            if pos.get("symbol") == "XRP-USDT" and float(pos.get("positionAmt", 0)) != 0:
                target = pos
                break
        
        if not target:
            print("❌ Позиция XRP-USDT не найдена")
            return
        
        side = target.get("positionSide")
        quantity = abs(float(target.get("positionAmt", 0)))
        entry = float(target.get("entryPrice", 0))
        
        tp_side = "SELL" if side == "LONG" else "BUY"
        
        # Рассчитываем 3 TP
        if side == "LONG":
            tp_prices = [
                round(entry * 1.02, 4),
                round(entry * 1.03, 4),
                round(entry * 1.05, 4)
            ]
        else:
            tp_prices = [
                round(entry * 0.98, 4),
                round(entry * 0.97, 4),
                round(entry * 0.95, 4)
            ]
        
        print(f"\n📊 Позиция: {side} {quantity} XRP @ ${entry:.4f}")
        print(f"🎯 TP цены: {tp_prices}")
        
        confirm = input("\n⚠️  Установить 3 TP? (да/нет): ").strip().lower()
        
        if confirm == 'да':
            result = await set_tp_orders(
                api_key=api_key,
                secret_key=secret_key,
                symbol="XRP-USDT",
                side=tp_side,
                quantity=quantity,
                tp_prices=tp_prices
            )
            
            print(f"\n✅ Результат: {result}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 ТЕСТИРОВАНИЕ МНОЖЕСТВЕННЫХ ТЕЙК-ПРОФИТОВ")
    print("=" * 70)
    print("\nВыберите режим тестирования:")
    print("1. Быстрый тест с множественными TP")
    print("2. Простой тест с 3 TP")
    print("3. Только проверка ордеров")
    
    mode = input("\nВаш выбор (1-3): ").strip()
    
    if mode == "1":
        asyncio.run(quick_multiple_tp_test())
    elif mode == "2":
        asyncio.run(test_simple_case())
    elif mode == "3":
        asyncio.run(check_tp_orders_after_test())
    else:
        print("❌ Неверный выбор")