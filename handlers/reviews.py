from aiogram import Router, F
from aiogram.types import Message
from database import Database

router = Router()
db = Database()

@router.message(F.text == "Отзывы")
async def show_random_review(message: Message):
    review = await db.get_random_review()
    if not review:
        await message.answer("Пока нет отзывов")
        return
    
    text, photo_file_id = review
    if photo_file_id:
        await message.answer_photo(photo=photo_file_id, caption=text)
    else:
        await message.answer(text)
