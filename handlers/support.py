from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import SupportStates
from database import Database
from config import ADMIN_ID

router = Router()
db = Database()

@router.message(F.text == "💬 Поддержка")
async def ask_support(message: Message, state: FSMContext):
    await message.answer("Напишите ваше сообщение для поддержки (вы также можете прикрепить 1 фото):")
    await state.set_state(SupportStates.waiting_for_message)

@router.message(SupportStates.waiting_for_message)
async def process_support_message(message: Message, state: FSMContext):
    text = message.text or message.caption or "Без текста"
    photo_id = message.photo[-1].file_id if message.photo else None
    
    msg_id = await db.save_support_message(message.from_user.id, text, photo_id)
    
    await message.answer("Ваше сообщение отправлено. Мы ответим вам в ближайшее время.")
    await state.clear()
    
    from keyboards import get_admin_support_keyboard
    bot = message.bot
    admin_text = f"Новое обращение (Анонимный ID: {msg_id}):\n\n{text}"
    if photo_id:
        await bot.send_photo(ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=get_admin_support_keyboard(msg_id))
    else:
        await bot.send_message(ADMIN_ID, text=admin_text, reply_markup=get_admin_support_keyboard(msg_id))
