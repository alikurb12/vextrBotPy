import asyncio
import sys
import os

sys.path.append('.')

async def test_close_position():
    """Тестирование закрытия позиции по XRP-USDT"""
    
    try:
        from backend.exchange_apis.bingx.services.close_position import close_position
        from backend.exchange_apis.bingx.services.get_open_positions import get_open_positions
        
        print("🧪 Тестирование функции close_position")
        print("=" * 60)
        print("⚠️  ВНИМАНИЕ: Этот тест ЗАКРОЕТ вашу открытую позицию по XRP-USDT!")
        print("=" * 60)
        
        # Запросим подтверждение
        confirmation = input("\nУ вас есть открытая позиция по XRP-USDT? (да/нет): ").strip().lower()
        if confirmation != 'да':
            print("❌ Тест отменен пользователем")
            return
        
        confirmation2 = input("Вы точно хотите ЗАКРЫТЬ позицию по XRP-USDT? (да/нет): ").strip().lower()
        if confirmation2 != 'да':
            print("❌ Тест отменен пользователем")
            return
        
        # Запросим API ключи
        api_key = input("\nВведите API ключ BingX: ").strip()
        secret_key = input("Введите Secret ключ BingX: ").strip()
        
        if not api_key or not secret_key:
            print("❌ API ключи не указаны")
            return
        
        print(f"\n🔑 Тестирование с API ключом: {api_key[:10]}...")
        print("-" * 40)
        
        try:
            # 1. Сначала проверим открытые позиции
            print("1. Проверка открытых позиций...")
            positions_before = await get_open_positions(api_key, secret_key)
            
            # Ищем позицию по XRP
            xrp_position = None
            for pos in positions_before:
                if pos.get("symbol") == "XRP-USDT":
                    position_amt = float(pos.get("positionAmt", 0))
                    if position_amt != 0:
                        xrp_position = pos
                        break
            
            if not xrp_position:
                print("❌ Позиция по XRP-USDT не найдена!")
                print("   Убедитесь, что у вас открыта позиция по XRP")
                return
            
            # Показываем информацию о позиции
            print(f"\n✅ Найдена позиция по XRP-USDT:")
            print(f"   • Сторона: {xrp_position.get('positionSide', 'N/A')}")
            print(f"   • Объем: {float(xrp_position.get('positionAmt', 0))}")
            print(f"   • Цена входа: ${float(xrp_position.get('entryPrice', 0)):,.4f}")
            print(f"   • Текущая цена: ${float(xrp_position.get('markPrice', 0)):,.4f}")
            print(f"   • PnL: ${float(xrp_position.get('unRealizedProfit', 0)):,.4f}")
            
            # 2. Закрываем позицию
            print(f"\n2. Закрываем позицию по XRP-USDT...")
            
            close_result = await close_position("XRP-USDT", api_key, secret_key)
            
            if close_result:
                print(f"✅ Позиция успешно закрыта!")
                print(f"   Результат: {close_result}")
            else:
                print(f"❌ Не удалось закрыть позицию")
                return
            
            # 3. Проверяем, что позиция действительно закрыта
            print(f"\n3. Проверка после закрытия...")
            
            # Даем время на обработку
            await asyncio.sleep(2)
            
            positions_after = await get_open_positions(api_key, secret_key)
            
            # Ищем позицию по XRP
            xrp_closed = True
            for pos in positions_after:
                if pos.get("symbol") == "XRP-USDT":
                    position_amt = float(pos.get("positionAmt", 0))
                    if position_amt != 0:
                        xrp_closed = False
                        print(f"⚠️  Позиция все еще открыта! Объем: {position_amt}")
                        break
            
            if xrp_closed:
                print(f"✅ Позиция успешно закрыта (подтверждено)")
            else:
                print(f"⚠️  Позиция не закрылась, попробуйте еще раз")
            
        except ValueError as e:
            print(f"❌ Ошибка API: {e}")
            
            # Диагностика ошибок
            error_str = str(e).lower()
            if "position" in error_str and "not exist" in error_str:
                print("   Позиция уже закрыта или не существует")
            elif "timestamp" in error_str:
                print("   Проблема с синхронизацией времени")
            elif "signature" in error_str:
                print("   Проблема с подписью запроса")
            elif "api" in error_str and "key" in error_str:
                print("   Проблема с API ключами")
            elif "balance" in error_str:
                print("   Недостаточно средств для комиссии")
                
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("✅ Тест завершен")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверьте пути импорта:")
        print("1. Файл close_position.py существует")
        print("2. Файлы get_open_positions.py, get_sign.py, parseParam.py существуют")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_close_position())