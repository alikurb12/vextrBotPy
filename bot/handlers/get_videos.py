# @dp.message(Command("get_video_bingx"))
# async def get_photo(message: Message):
#     current_dir = Path(__file__).parent
#     video_path = current_dir / "videos" / "bingx.mp4"

#     if not video_path.exists():
#         await message.answer("Видео не найдено")
    
#     try:
#         video = FSInputFile(video_path)
#         await message.answer_video(
#             video=video,
#             caption="Вот инструкция для подключение API из биржи BingX"
#         )
#     except Exception as e:
#         await message.answer(f"Ошибка при отправке видео {e}")