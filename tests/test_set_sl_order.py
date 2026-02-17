#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
БЫСТРЫЙ ТЕСТ ДЛЯ УСТАНОВКИ СТОП-ЛОССА
Запуск: python quick_sl_test.py
"""

import asyncio
import sys
import os
sys.path.append('.')

async def quick_sl_test():
    """Быстрый тест установки стоп-лосса"""
    
    print("=" * 60)
    print("🚀 БЫСТРЫЙ ТЕСТ УСТАНОВКИ СТОП-ЛОССА")
    print("=" * 60)
    
    try:
        from backend.exchange_apis.bingx.services.set_sl_order import set_sl_order
        from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return
    
    # Ввод ключей
    api_key = input("\n🔑 API ключ: ").strip()
    secret_key = input("🔑 Secret ключ: ").strip()
    
    if not api_key or not secret_key:
        print("❌ Ключи не указаны")
        return
    
    # Получаем позиции
    print("\n📊 Получаем открытые позиции...")
    positions = await get_open_positions(api_key, secret_key)
    
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
        print(f"{i}. {symbol} {side}: {amt} @ ${entry:.4f}")
    
    # Выбор позиции
    choice = input("\n🎯 Выберите номер позиции: ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(active):
            pos = active[idx]
            symbol = pos.get("symbol")
            side = pos.get("positionSide")
            quantity = abs(float(pos.get("positionAmt", 0)))
            
            # Определяем сторону для SL
            sl_side = "SELL" if side == "LONG" else "BUY"
            
            print(f"\n📊 ПОЗИЦИЯ: {symbol} {side}")
            print(f"   Количество: {quantity}")
            print(f"   SL сторона: {sl_side}")
            
            # Ввод цены
            sl_price = float(input("\n💰 Цена стоп-лосса: ").strip())
            
            # Подтверждение
            print(f"\n📋 ПАРАМЕТРЫ ОРДЕРА:")
            print(f"   • Символ: {symbol}")
            print(f"   • Тип: STOP_MARKET")
            print(f"   • Сторона: {sl_side}")
            print(f"   • PositionSide: {side}")
            print(f"   • Количество: {quantity}")
            print(f"   • Цена SL: ${sl_price:.4f}")
            
            confirm = input("\n⚠️  УСТАНОВИТЬ? (да/нет): ").strip().lower()
            
            if confirm == 'да':
                result = await set_sl_order(
                    api_key=api_key,
                    secret_key=secret_key,
                    symbol=symbol,
                    price=sl_price,
                    side=sl_side,
                    quantity=quantity
                )
                
                print(f"\n✅ СТОП-ЛОСС УСТАНОВЛЕН!")
                print(f"📦 Order ID: {result.get('order', {}).get('orderId')}")
            else:
                print("❌ Отменено")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(quick_sl_test())