from aiogram import Router, F
from aiogram.types import Message
from keyboards import get_main_menu

router = Router()

@router.message(F.text == "В меню")
async def go_to_menu(message: Message):
    await message.answer("Вы вернулись в главное меню", reply_markup=get_main_menu())
