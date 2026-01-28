from pathlib import Path
from aiogram.types import CallbackQuery, FSInputFile

current_dir = Path(__file__).parent

async def send_video_instruction(callback_query: CallbackQuery, video_filename: str, caption: str):
    video_path = current_dir / "videos" / video_filename
    
    if video_path.exists():
        try:
            video = FSInputFile(video_path)
            await callback_query.message.answer_video(
                video=video,
                caption=caption
            )
        except Exception as e:
            await callback_query.message.answer(
                f"❌ Не удалось отправить видео: {str(e)[:100]}"
            )
    else:
        await callback_query.message.answer(
            f"❌ Файл инструкции не найден: {video_filename}"
        )