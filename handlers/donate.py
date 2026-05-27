from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import DONATE_TEXT, DONATE_IMAGE_FILE_ID, DONATE_URL

router = Router()

@router.message(F.text == "Донат")
async def show_donate(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Поддержать", url=DONATE_URL)]]
    )
    await message.answer_photo(
        photo=DONATE_IMAGE_FILE_ID,
        caption=DONATE_TEXT,
        reply_markup=keyboard
    )
