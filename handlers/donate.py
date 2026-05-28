from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import DONATE_TEXT, DONATE_IMAGE_FILE_ID, DONATE_URL

router = Router()

@router.message(F.text == "Донат")
async def show_donate(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Поддержать", url=DONATE_URL)]]
    )
    try:
        from aiogram.types import URLInputFile
        photo_obj = URLInputFile(DONATE_IMAGE_FILE_ID) if DONATE_IMAGE_FILE_ID.startswith("http") else DONATE_IMAGE_FILE_ID
        await message.answer_photo(
            photo=photo_obj,
            caption=DONATE_TEXT,
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Donate photo error: {e}")
        await message.answer(
            text=DONATE_TEXT,
            reply_markup=keyboard
        )
