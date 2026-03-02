import asyncio
import sys
import os

sys.path.append('.')

async def test_set_leverage_5x():
    """Тестирование установки плеча 5x для XRP-USDT"""
    
    try:
        from backend.exchange_apis.bingx.services.set_leverage import set_leverage
        from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions
        
        print("🧪 Тестирование функции set_leverage (плечо 5x)")
        print("=" * 60)
        print("ℹ️  Эта функция устанавливает плечо 5x для указанной стороны")
        print("=" * 60)
        
        # Запросим API ключи
        api_key = input("\nВведите API ключ BingX: ").strip()
        secret_key = input("Введите Secret ключ BingX: ").strip()
        
        if not api_key or not secret_key:
            print("❌ API ключи не указаны")
            return
        
        symbol = "XRP-USDT"
        
        print(f"\n🔑 Тестирование с API ключом: {api_key[:10]}...")
        print(f"📊 Символ: {symbol}")
        print("-" * 40)
        
        try:
            # 1. Сначала проверим текущее плечо
            print("1. Проверяем текущее плечо...")
            positions = await get_open_positions(api_key, secret_key)
            
            current_long = None
            current_short = None
            
            for pos in positions:
                if pos.get("symbol") == symbol:
                    side = pos.get("positionSide")
                    leverage = pos.get("leverage")
                    
                    if side == "LONG":
                        current_long = leverage
                        print(f"   📈 Текущее плечо LONG: {leverage}x")
                    elif side == "SHORT":
                        current_short = leverage
                        print(f"   📉 Текущее плечо SHORT: {leverage}x")
            
            # 2. Тестируем установку для LONG
            print("\n2. Тестируем установку плеча 5x для LONG...")
            try:
                result_long = await set_leverage(
                    symbol=symbol,
                    side="LONG",
                    api_key=api_key,
                    secret_key=secret_key
                )
                
                print("   ✅ Плечо 5x для LONG установлено")
                if result_long:
                    print(f"      Ответ API: {result_long}")
                    
            except ValueError as e:
                print(f"   ❌ Ошибка: {e}")
                
                # Анализ ошибки
                if "position" in str(e).lower() and "exist" in str(e).lower():
                    print("      ⚠️  Возможно, у вас уже есть открытая позиция LONG")
            
            await asyncio.sleep(1)
            
            # 3. Тестируем установку для SHORT
            print("\n3. Тестируем установку плеча 5x для SHORT...")
            try:
                result_short = await set_leverage(
                    symbol=symbol,
                    side="SHORT",
                    api_key=api_key,
                    secret_key=secret_key
                )
                
                print("   ✅ Плечо 5x для SHORT установлено")
                if result_short:
                    print(f"      Ответ API: {result_short}")
                    
            except ValueError as e:
                print(f"   ❌ Ошибка: {e}")
                
                if "position" in str(e).lower() and "exist" in str(e).lower():
                    print("      ⚠️  Возможно, у вас уже есть открытая позиция SHORT")
            
            await asyncio.sleep(1)
            
            # 4. Тестируем с неправильными параметрами
            print("\n4. Тестируем некорректные параметры...")
            
            # Неверный символ
            print("\n   🔄 Неверный символ:")
            try:
                await set_leverage(
                    symbol="INVALID-SYMBOL",
                    side="LONG",
                    api_key=api_key,
                    secret_key=secret_key
                )
                print("   ❌ Должна была возникнуть ошибка")
            except ValueError as e:
                print(f"   ✅ Ожидаемая ошибка: {e}")
            
            # Неверная сторона
            print("\n   🔄 Неверная сторона:")
            try:
                await set_leverage(
                    symbol=symbol,
                    side="INVALID",
                    api_key=api_key,
                    secret_key=secret_key
                )
                print("   ❌ Должна была возникнуть ошибка")
            except ValueError as e:
                print(f"   ✅ Ожидаемая ошибка: {e}")
            
            # 5. Проверяем, что плечо действительно 5x
            print("\n5. Проверяем установленное плечо...")
            
            # Получаем обновленные данные
            positions_after = await get_open_positions(api_key, secret_key)
            
            long_after = None
            short_after = None
            
            for pos in positions_after:
                if pos.get("symbol") == symbol:
                    side = pos.get("positionSide")
                    leverage = pos.get("leverage")
                    
                    if side == "LONG":
                        long_after = leverage
                        print(f"   📈 Плечо LONG сейчас: {leverage}x")
                        if leverage == 5:
                            print(f"      ✅ LONG установлено 5x")
                        else:
                            print(f"      ⚠️  LONG: ожидалось 5x, получено {leverage}x")
                    
                    elif side == "SHORT":
                        short_after = leverage
                        print(f"   📉 Плечо SHORT сейчас: {leverage}x")
                        if leverage == 5:
                            print(f"      ✅ SHORT установлено 5x")
                        else:
                            print(f"      ⚠️  SHORT: ожидалось 5x, получено {leverage}x")
            
            # 6. Итоговый отчет
            print("\n" + "=" * 60)
            print("📊 ИТОГОВЫЙ ОТЧЕТ:")
            print(f"Символ: {symbol}")
            
            if long_after:
                print(f"LONG: {long_after}x {'✅' if long_after == 5 else '⚠️'}")
            if short_after:
                print(f"SHORT: {short_after}x {'✅' if short_after == 5 else '⚠️'}")
            
            if not long_after and not short_after:
                print("ℹ️  Нет открытых позиций для проверки плеча")
            
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("✅ Тест завершен")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверьте пути импорта:")
        print("1. Файл set_leverage.py существует")
        print("2. Файлы get_sign.py и parseParam.py существуют")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_set_leverage_5x())