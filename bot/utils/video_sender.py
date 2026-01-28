from pathlib import Path
from aiogram.types import FSInputFile
from aiogram.types import CallbackQuery

BASE_DIR = Path(__file__).parent.parent
VIDEOS_DIR = BASE_DIR / "videos"

async def send_video_instruction(callback_query: CallbackQuery, video_filename: str, caption: str):
    video_path = VIDEOS_DIR / video_filename
    if not VIDEOS_DIR.exists():
        await callback_query.message.answer("❌ Папка с видео не найдена")
        return
    
    if video_path.exists():
        try:
            video = FSInputFile(video_path)
            await callback_query.message.answer_video(
                video=video,
                caption=caption
            )
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await callback_query.message.answer(
                f"❌ Ошибка при отправке видео: {str(e)[:100]}"
            )
    else:
        await callback_query.message.answer(
            f"❌ Видеоинструкция '{video_filename}' не найдена.\n"
        )