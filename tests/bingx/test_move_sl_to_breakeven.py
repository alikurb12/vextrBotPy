#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ТЕСТ ДЛЯ ФУНКЦИИ move_sl_to_breakeven (ПЕРЕНОС СТОП-ЛОССА К ЦЕНЕ ВХОДА)
Запуск: python test_move_sl_to_breakeven.py
"""

import asyncio
import sys
import os
import json
from typing import Optional, Dict, Any

sys.path.append('.')

async def get_current_price(symbol: str) -> Optional[float]:
    """Получает текущую цену для расчетов"""
    import httpx
    try:
        url = f"https://open-api.bingx.com/openApi/swap/v2/quote/price?symbol={symbol}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            if data.get("code") == 0:
                return float(data.get("data", {}).get("price", 0))
    except Exception as e:
        print(f"⚠️ Ошибка получения цены: {e}")
    return None


async def get_open_position_for_symbol(api_key: str, secret_key: str, symbol: str) -> Optional[Dict[str, Any]]:
    """Получает открытую позицию по символу"""
    try:
        from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions
        
        print("📊 Получаем открытые позиции...")
        positions = await get_open_positions(api_key, secret_key)
        
        if not positions:
            print("❌ Нет открытых позиций")
            return None
        
        for pos in positions:
            pos_symbol = pos.get("symbol")
            pos_amt = float(pos.get("positionAmt", 0))
            
            if pos_symbol == symbol and pos_amt != 0:
                print(f"✅ Найдена позиция {symbol}")
                return pos
        
        print(f"❌ Позиция {symbol} не найдена")
        return None
        
    except Exception as e:
        print(f"❌ Ошибка получения позиции: {e}")
        return None


async def get_open_orders_for_symbol(api_key: str, secret_key: str, symbol: str) -> list:
    """Получает открытые ордера по символу"""
    try:
        from backend.exchange_apis.bingx.services.get_open_orders import get_open_orders
        
        orders_data = await get_open_orders(api_key, secret_key)
        if orders_data:
            orders = orders_data.get('orders', [])
            return [o for o in orders if o.get('symbol') == symbol]
        return []
        
    except Exception as e:
        print(f"⚠️ Ошибка получения ордеров: {e}")
        return []


async def get_sl_order_id(api_key: str, secret_key: str, symbol: str) -> Optional[int]:
    """Находит ID существующего SL ордера"""
    orders = await get_open_orders_for_symbol(api_key, secret_key, symbol)
    
    sl_orders = [o for o in orders if o.get('type') == 'STOP_MARKET']
    
    if not sl_orders:
        print("ℹ️ Нет активных SL ордеров")
        return None
    
    if len(sl_orders) > 1:
        print(f"⚠️ Найдено несколько SL ордеров: {len(sl_orders)}")
        for i, order in enumerate(sl_orders, 1):
            print(f"   {i}. ID: {order.get('orderId')}, Цена: ${float(order.get('stopPrice', 0)):.4f}")
        
        choice = input("Выберите номер SL ордера для теста: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sl_orders):
                return int(sl_orders[idx].get('orderId'))
        except:
            pass
    
    return int(sl_orders[0].get('orderId'))


async def create_test_sl_order(api_key: str, secret_key: str, symbol: str, side: str, quantity: float, price: float) -> Optional[int]:
    """Создает тестовый SL ордер"""
    try:
        from backend.exchange_apis.bingx.services.set_sl_order import set_sl_order
        
        print(f"\n🔄 Создаем тестовый SL ордер...")
        result = await set_sl_order(
            api_key=api_key,
            secret_key=secret_key,
            symbol=symbol,
            price=price,
            side=side,
            quantity=quantity
        )
        
        order_id = result.get('order', {}).get('orderId')
        print(f"✅ Создан тестовый SL ордер ID: {order_id}")
        return order_id
        
    except Exception as e:
        print(f"❌ Ошибка создания тестового SL: {e}")
        return None


async def test_move_sl_to_breakeven():
    """
    ПОЛНОЕ ТЕСТИРОВАНИЕ ФУНКЦИИ move_sl_to_breakeven
    """
    
    try:
        from backend.exchange_apis.bingx.services.move_sl_to_breakeven import move_sl_to_breakeven
        
        print("=" * 80)
        print("🧪 ТЕСТИРОВАНИЕ ФУНКЦИИ move_sl_to_breakeven")
        print("=" * 80)
        print("⚠️  ВНИМАНИЕ: Этот тест отменит существующий SL и создаст новый!")
        print("=" * 80)
        
        # Ввод ключей
        print("\n🔑 ВВОД API КЛЮЧЕЙ")
        print("-" * 40)
        
        api_key = input("Введите API ключ BingX: ").strip()
        secret_key = input("Введите Secret ключ BingX: ").strip()
        
        if not api_key or not secret_key:
            print("❌ API ключи не указаны")
            return
        
        # Выбор символа
        symbol = input("\n💱 Введите символ (по умолчанию XRP-USDT): ").strip().upper()
        if not symbol:
            symbol = "XRP-USDT"
        
        # Получаем текущую цену
        current_price = await get_current_price(symbol)
        if current_price:
            print(f"\n💰 Текущая цена {symbol}: ${current_price:.4f}")
        
        # Получаем позицию
        position = await get_open_position_for_symbol(api_key, secret_key, symbol)
        
        if position:
            side = position.get("positionSide")
            quantity = abs(float(position.get("positionAmt", 0)))
            entry_price = float(position.get("entryPrice", 0)) or float(position.get("avgPrice", 0))
            mark_price = float(position.get("markPrice", 0))
            
            print(f"\n📊 НАЙДЕНА ПОЗИЦИЯ:")
            print(f"   • Сторона: {side}")
            print(f"   • Количество: {quantity}")
            print(f"   • Цена входа: ${entry_price:.4f}")
            print(f"   • Текущая цена: ${mark_price:.4f}")
            
            # Рассчитываем текущую прибыль
            if side == "LONG":
                profit_pct = ((mark_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
            else:
                profit_pct = ((entry_price - mark_price) / entry_price) * 100 if entry_price > 0 else 0
            
            print(f"   • Прибыль: {profit_pct:+.2f}%")
            
            # Проверяем, достаточно ли прибыли для breakeven
            if profit_pct <= 0:
                print(f"\n⚠️  ВНИМАНИЕ: Позиция не в прибыли ({profit_pct:+.2f}%)")
                print("   Перенос SL к цене входа может привести к немедленному срабатыванию")
                confirm = input("   Продолжить? (да/нет): ").strip().lower()
                if confirm != 'да':
                    print("❌ Тест отменен")
                    return
            
            # Определяем сторону для SL
            sl_side = "SELL" if side == "LONG" else "BUY"
            
            # Проверяем существующие SL ордера
            print("\n🔍 ПРОВЕРКА СУЩЕСТВУЮЩИХ SL ОРДЕРОВ")
            print("-" * 40)
            
            existing_sl_id = await get_sl_order_id(api_key, secret_key, symbol)
            
            if not existing_sl_id:
                print("\n⚠️ НЕТ АКТИВНЫХ SL ОРДЕРОВ")
                print("   Для теста нужно создать SL ордер")
                
                create_new = input("   Создать тестовый SL ордер? (да/нет): ").strip().lower()
                
                if create_new == 'да':
                    # Рассчитываем цену для тестового SL
                    if side == "LONG":
                        test_sl_price = round(mark_price * 0.95, 4)  # 5% ниже текущей
                    else:
                        test_sl_price = round(mark_price * 1.05, 4)  # 5% выше текущей
                    
                    print(f"\n📋 БУДЕТ СОЗДАН ТЕСТОВЫЙ SL ОРДЕР:")
                    print(f"   • Цена: ${test_sl_price:.4f}")
                    print(f"   • Количество: {quantity}")
                    
                    confirm = input("   Продолжить? (да/нет): ").strip().lower()
                    
                    if confirm == 'да':
                        existing_sl_id = await create_test_sl_order(
                            api_key=api_key,
                            secret_key=secret_key,
                            symbol=symbol,
                            side=sl_side,
                            quantity=quantity,
                            price=test_sl_price
                        )
                        
                        if not existing_sl_id:
                            print("❌ Не удалось создать тестовый SL")
                            return
                        
                        print(f"\n⏳ Ожидаем 2 секунды...")
                        await asyncio.sleep(2)
                    else:
                        print("❌ Тест отменен")
                        return
                else:
                    print("❌ Тест отменен")
                    return
            
            print(f"\n🎯 НАЙДЕН SL ОРДЕР ДЛЯ ТЕСТА:")
            print(f"   • Order ID: {existing_sl_id}")
            
            # Получаем информацию о текущем SL
            orders = await get_open_orders_for_symbol(api_key, secret_key, symbol)
            current_sl = None
            for order in orders:
                if order.get('orderId') == existing_sl_id:
                    current_sl = order
                    break
            
            if current_sl:
                current_sl_price = float(current_sl.get('stopPrice', 0))
                print(f"   • Текущая цена SL: ${current_sl_price:.4f}")
            
            print(f"\n📋 ПАРАМЕТРЫ ДЛЯ move_sl_to_breakeven:")
            print(f"   • Символ: {symbol}")
            print(f"   • Сторона: {side}")
            print(f"   • Количество: {quantity}")
            print(f"   • Цена входа: ${entry_price:.4f}")
            print(f"   • SL Order ID: {existing_sl_id}")
            
            print("\n⚠️  БУДЕТ ВЫПОЛНЕНО:")
            print("   1. Отмена существующего SL ордера")
            print("   2. Создание нового SL ордера по цене входа")
            
            confirm = input("\n⚠️  ПРОДОЛЖИТЬ ТЕСТ? (да/нет): ").strip().lower()
            
            if confirm == 'да':
                try:
                    print("\n" + "=" * 60)
                    print("🔄 ВЫПОЛНЕНИЕ move_sl_to_breakeven")
                    print("=" * 60)
                    
                    start_time = asyncio.get_event_loop().time()
                    
                    result = await move_sl_to_breakeven(
                        api_key=api_key,
                        secret_key=secret_key,
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        entry_price=entry_price,
                        sl_order_id=existing_sl_id
                    )
                    
                    elapsed_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    print(f"\n✅ ОПЕРАЦИЯ ВЫПОЛНЕНА ЗА {elapsed_time:.0f} МС")
                    
                    print(f"\n📦 РЕЗУЛЬТАТ:")
                    if result and 'order' in result:
                        new_order = result['order']
                        print(f"   • Новый SL Order ID: {new_order.get('orderId')}")
                        print(f"   • Цена: ${float(new_order.get('stopPrice', 0)):.4f}")
                        print(f"   • Количество: {new_order.get('quantity')}")
                    else:
                        print(f"   {result}")
                    
                    # Проверяем результат
                    print("\n🔍 ПРОВЕРКА РЕЗУЛЬТАТА")
                    print("-" * 40)
                    
                    await asyncio.sleep(2)
                    
                    # Проверяем, что старый SL отменен
                    orders_after = await get_open_orders_for_symbol(api_key, secret_key, symbol)
                    
                    old_sl_exists = any(o.get('orderId') == existing_sl_id for o in orders_after)
                    if old_sl_exists:
                        print(f"⚠️ Старый SL ордер {existing_sl_id} все еще существует!")
                    else:
                        print(f"✅ Старый SL ордер {existing_sl_id} успешно отменен")
                    
                    # Проверяем новый SL
                    new_sl_orders = [o for o in orders_after if o.get('type') == 'STOP_MARKET']
                    
                    if new_sl_orders:
                        print(f"✅ Новый SL ордер создан:")
                        for order in new_sl_orders:
                            order_price = float(order.get('stopPrice', 0))
                            print(f"   • ID: {order.get('orderId')}")
                            print(f"   • Цена: ${order_price:.4f}")
                            print(f"   • Количество: {order.get('quantity')}")
                            
                            # Проверяем, что цена близка к entry_price
                            price_diff = abs(order_price - entry_price)
                            if price_diff < 0.001:
                                print(f"   ✅ Цена совпадает с ценой входа")
                            else:
                                print(f"   ⚠️ Цена отличается от входа на ${price_diff:.4f}")
                    else:
                        print(f"❌ Новый SL ордер не найден!")
                    
                except ValueError as e:
                    print(f"\n❌ ОШИБКА: {e}")
                    
                    # Анализ ошибки
                    error_str = str(e).lower()
                    if "position not exist" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Убедитесь, что у вас есть открытая позиция")
                    elif "order not exist" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Указанный SL ордер не существует")
                        print(f"   • Order ID: {existing_sl_id}")
                    elif "cancel" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Ошибка при отмене ордера")
                    elif "set_sl" in error_str:
                        print("\n🔍 ДИАГНОСТИКА:")
                        print("   • Ошибка при создании нового SL")
                
                except Exception as e:
                    print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ Тест отменен")
                
        else:
            print(f"\n❌ Нет открытой позиции по {symbol}")
            print("   Тест требует существующую позицию для выполнения")
            
    except ImportError as e:
        print(f"❌ ОШИБКА ИМПОРТА: {e}")
        print("\n🔍 ПРОВЕРЬТЕ:")
        print("   1. Файл move_sl_to_breakeven.py существует")
        print("   2. Файлы cancel_order.py и set_sl_order.py существуют")
    except KeyboardInterrupt:
        print("\n\n⚠️ ТЕСТ ПРЕРВАН ПОЛЬЗОВАТЕЛЕМ")
    except Exception as e:
        print(f"❌ НЕОЖИДАННАЯ ОШИБКА: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def test_cancel_order_only():
    """Тест только функции cancel_order"""
    
    try:
        from backend.exchange_apis.bingx.services.move_sl_to_breakeven import cancel_order
        
        print("=" * 60)
        print("🧪 ТЕСТ ФУНКЦИИ cancel_order (только отмена)")
        print("=" * 60)
        
        api_key = input("\n🔑 API ключ: ").strip()
        secret_key = input("🔑 Secret ключ: ").strip()
        symbol = input("💱 Символ: ").strip().upper()
        order_id = int(input("🆔 Order ID для отмены: ").strip())
        
        confirm = input(f"\n⚠️  Отменить ордер {order_id}? (да/нет): ").strip().lower()
        
        if confirm == 'да':
            try:
                result = await cancel_order(
                    api_key=api_key,
                    secret_key=secret_key,
                    symbol=symbol,
                    order_id=order_id
                )
                print(f"\n✅ Ордер отменен!")
                print(f"📦 Результат: {result}")
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
        else:
            print("❌ Тест отменен")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


async def quick_test():
    """Быстрый тест для проверки"""
    
    print("=" * 60)
    print("🚀 БЫСТРЫЙ ТЕСТ move_sl_to_breakeven")
    print("=" * 60)
    print("\n⚠️  Для этого теста нужна:")
    print("   1. Открытая позиция")
    print("   2. Активный SL ордер")
    print("=" * 60)
    
    try:
        from backend.exchange_apis.bingx.services.move_sl_to_breakeven import move_sl_to_breakeven
        from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions
        from backend.exchange_apis.bingx.services.get_open_orders import get_open_orders
        
        api_key = input("\n🔑 API ключ: ").strip()
        secret_key = input("🔑 Secret ключ: ").strip()
        
        if not api_key or not secret_key:
            print("❌ Ключи не указаны")
            return
        
        symbol = input("💱 Символ (по умолчанию XRP-USDT): ").strip().upper()
        if not symbol:
            symbol = "XRP-USDT"
        
        # Получаем позицию
        position = await get_open_position_for_symbol(api_key, secret_key, symbol)
        
        if not position:
            print(f"❌ Нет позиции {symbol}")
            return
        
        side = position.get("positionSide")
        quantity = abs(float(position.get("positionAmt", 0)))
        entry_price = float(position.get("entryPrice", 0)) or float(position.get("avgPrice", 0))
        
        # Получаем SL ордер
        sl_id = await get_sl_order_id(api_key, secret_key, symbol)
        
        if not sl_id:
            print("❌ Нет SL ордера для теста")
            return
        
        print(f"\n📋 ПАРАМЕТРЫ:")
        print(f"   • Позиция: {side}")
        print(f"   • Количество: {quantity}")
        print(f"   • Цена входа: ${entry_price:.4f}")
        print(f"   • SL Order ID: {sl_id}")
        
        confirm = input("\n⚠️  Выполнить move_sl_to_breakeven? (да/нет): ").strip().lower()
        
        if confirm == 'да':
            result = await move_sl_to_breakeven(
                api_key=api_key,
                secret_key=secret_key,
                symbol=symbol,
                side=side,
                quantity=quantity,
                entry_price=entry_price,
                sl_order_id=sl_id
            )
            
            print(f"\n✅ Результат: {result}")
        else:
            print("❌ Тест отменен")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🧪 ТЕСТИРОВАНИЕ move_sl_to_breakeven")
    print("=" * 80)
    print("\nВыберите режим тестирования:")
    print("1. Полный тест move_sl_to_breakeven")
    print("2. Тест только cancel_order")
    print("3. Быстрый тест")
    
    mode = input("\nВаш выбор (1-3): ").strip()
    
    if mode == "1":
        asyncio.run(test_move_sl_to_breakeven())
    elif mode == "2":
        asyncio.run(test_cancel_order_only())
    elif mode == "3":
        asyncio.run(quick_test())
    else:
        print("❌ Неверный выбор")