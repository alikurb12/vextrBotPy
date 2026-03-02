import asyncio
import sys
import os
sys.path.append('.')

async def quick_tp_test():
    """Быстрый тест установки тейк-профита"""
    
    print("=" * 60)
    print("🚀 БЫСТРЫЙ ТЕСТ УСТАНОВКИ ТЕЙК-ПРОФИТА")
    print("=" * 60)
    
    try:
        from backend.exchange_apis.bingx.services.set_tp_orders import set_tp_orders
        from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("\n🔍 Проверьте:")
        print("   1. Файл set_tp_orders.py существует в backend/exchange_apis/bingx/services/")
        print("   2. Файл get_open_positions.py существует")
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
        entry = float(pos.get("avgPrice", 0))
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
            # Для LONG позиции: side = "SELL" (продаем для фиксации прибыли)
            # Для SHORT позиции: side = "BUY" (покупаем для фиксации прибыли)
            tp_side = "SELL" if side == "LONG" else "BUY"
            
            print(f"\n📊 ПОЗИЦИЯ: {symbol} {side}")
            print(f"   Количество: {quantity}")
            print(f"   Цена входа: ${entry:.4f}")
            print(f"   Текущая цена: ${mark:.4f}")
            print(f"   TP сторона: {tp_side}")
            
            # Рассчитываем рекомендуемые цены
            if side == "LONG":
                tp1 = round(entry * 1.03, 4)   # +3%
                tp2 = round(entry * 1.05, 4)   # +5%
                tp3 = round(entry * 1.07, 4)   # +7%
                tp4 = round(entry * 1.10, 4)   # +10%
            else:  # SHORT
                tp1 = round(entry * 0.97, 4)   # -3%
                tp2 = round(entry * 0.95, 4)   # -5%
                tp3 = round(entry * 0.93, 4)   # -7%
                tp4 = round(entry * 0.90, 4)   # -10%
            
            print(f"\n💡 РЕКОМЕНДУЕМЫЕ ЦЕНЫ:")
            print(f"   TP1 (+3%):  ${tp1:.4f}")
            print(f"   TP2 (+5%):  ${tp2:.4f}")
            print(f"   TP3 (+7%):  ${tp3:.4f}")
            print(f"   TP4 (+10%): ${tp4:.4f}")
            
            # Ввод цены
            tp_price = float(input("\n💰 Цена тейк-профита: ").strip())
            
            # Проверка цены
            if side == "LONG" and tp_price <= mark:
                print(f"\n⚠️  ВНИМАНИЕ: Цена TP (${tp_price:.4f}) ниже текущей цены (${mark:.4f})")
                print("   Для LONG позиции TP должен быть выше текущей цены")
                confirm = input("   Продолжить все равно? (да/нет): ").strip().lower()
                if confirm != 'да':
                    print("❌ Отменено")
                    return
            elif side == "SHORT" and tp_price >= mark:
                print(f"\n⚠️  ВНИМАНИЕ: Цена TP (${tp_price:.4f}) выше текущей цены (${mark:.4f})")
                print("   Для SHORT позиции TP должен быть ниже текущей цены")
                confirm = input("   Продолжить все равно? (да/нет): ").strip().lower()
                if confirm != 'да':
                    print("❌ Отменено")
                    return
            
            # Подтверждение
            print(f"\n📋 ПАРАМЕТРЫ ОРДЕРА:")
            print(f"   • Символ: {symbol}")
            print(f"   • Тип: TAKE_PROFIT_MARKET")
            print(f"   • Сторона: {tp_side}")
            print(f"   • PositionSide: {side}")
            print(f"   • Количество: {quantity}")
            print(f"   • Цена TP: ${tp_price:.4f}")
            
            confirm = input("\n⚠️  УСТАНОВИТЬ ТЕЙК-ПРОФИТ? (да/нет): ").strip().lower()
            
            if confirm == 'да':
                try:
                    result = await set_tp_orders(
                        api_key=api_key,
                        secret_key=secret_key,
                        symbol=symbol,
                        side=tp_side,
                        quantity=quantity,
                        price=tp_price
                    )
                    
                    print(f"\n✅ ТЕЙК-ПРОФИТ УСТАНОВЛЕН!")
                    
                    if result and 'order' in result:
                        print(f"📦 Order ID: {result.get('order', {}).get('orderId')}")
                        print(f"📦 Client Order ID: {result.get('order', {}).get('clientOrderId')}")
                    else:
                        print(f"📦 Результат: {result}")
                    
                    # Проверяем созданный ордер
                    print("\n🔍 Проверяем созданный ордер...")
                    await asyncio.sleep(2)
                    
                    from backend.exchange_apis.bingx.services.get_open_orders import get_open_orders
                    orders_data = await get_open_orders(api_key, secret_key)
                    
                    if orders_data:
                        orders = orders_data.get('orders', [])
                        tp_orders = [o for o in orders if o.get('type') == 'TAKE_PROFIT_MARKET' and o.get('symbol') == symbol]
                        
                        if tp_orders:
                            print(f"   ✅ Найден TP ордер:")
                            for o in tp_orders:
                                print(f"      • ID: {o.get('orderId')}")
                                print(f"      • Цена: ${float(o.get('stopPrice', 0)):.4f}")
                                print(f"      • Количество: {o.get('quantity')}")
                        else:
                            print(f"   ⚠️ TP ордер не найден в списке открытых ордеров")
                    
                except ValueError as e:
                    print(f"\n❌ ОШИБКА: {e}")
                    
                    # Анализ ошибки
                    error_str = str(e).lower()
                    if "position not exist" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Убедитесь, что у вас есть открытая позиция")
                        print("   • Проверьте правильность symbol и side")
                        print(f"   • symbol: {symbol}, side: {side}, tp_side: {tp_side}")
                        print("   • Убедитесь, что quantity совпадает с размером позиции")
                    elif "quantity" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Проблема с количеством")
                        print("   • Убедитесь, что quantity > 0")
                        print(f"   • quantity: {quantity}")
                    elif "price" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Проблема с ценой")
                        print(f"   • Для {side} позиции цена должна быть {'выше' if side == 'LONG' else 'ниже'} текущей")
                        print(f"   • Текущая цена: ${mark:.4f}")
                        print(f"   • Ваша цена: ${tp_price:.4f}")
                    elif "stopPrice" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Проблема с параметром stopPrice")
                        print("   • Убедитесь, что цена указана правильно")
                
                except Exception as e:
                    print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ Отменено")
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
        
        print("\n" + "=" * 60)
        print("🔍 ПРОВЕРКА АКТИВНЫХ ТЕЙК-ПРОФИТ ОРДЕРОВ")
        print("=" * 60)
        
        api_key = input("\n🔑 API ключ (Enter для пропуска): ").strip()
        if not api_key:
            return
            
        secret_key = input("🔑 Secret ключ: ").strip()
        
        orders_data = await get_open_orders(api_key, secret_key)
        
        if orders_data:
            orders = orders_data.get('orders', [])
            tp_orders = [o for o in orders if o.get('type') == 'TAKE_PROFIT_MARKET']
            
            if tp_orders:
                print(f"\n📋 НАЙДЕНО ТЕЙК-ПРОФИТ ОРДЕРОВ: {len(tp_orders)}")
                for i, order in enumerate(tp_orders, 1):
                    print(f"\n{i}. {order.get('symbol')} {order.get('positionSide')}:")
                    print(f"   • ID: {order.get('orderId')}")
                    print(f"   • Цена TP: ${float(order.get('stopPrice', 0)):.4f}")
                    print(f"   • Количество: {order.get('quantity')}")
                    print(f"   • Статус: {order.get('status')}")
            else:
                print("\n✅ Нет активных тейк-профит ордеров")
    except Exception as e:
        print(f"⚠️ Ошибка проверки: {e}")

if __name__ == "__main__":
    asyncio.run(quick_tp_test())
    
    # Спрашиваем, хочет ли пользователь проверить ордера
    check = input("\n\n🔍 Проверить активные TP ордера? (да/нет): ").strip().lower()
    if check == 'да':
        asyncio.run(check_tp_orders_after_test())