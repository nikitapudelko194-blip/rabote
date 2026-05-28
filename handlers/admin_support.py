from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import AdminSupportStates
from database import Database
from config import ADMIN_ID
from utils.logger import log_action

router = Router()
db = Database()

router.message.filter(F.from_user.id == ADMIN_ID)
router.callback_query.filter(F.from_user.id == ADMIN_ID)

@router.message(Command("support"))
async def cmd_support(message: Message):
    args = message.text.split()
    if len(args) > 1 and args[1] == 'history' and len(args) == 3:
        msg_id = int(args[2])
        user_id = await db.get_anonymous_id(msg_id)
        if not user_id:
            await message.answer("Диалог не найден.")
            return
            
        history = await db.get_conversation_with_user(user_id)
        text = f"История диалога (Анонимный ID: {msg_id}):\n\n"
        for is_admin, msg_text, created_at in history:
            sender = "Админ" if is_admin else "Пользователь"
            text += f"[{created_at}] {sender}: {msg_text}\n"
        
        for i in range(0, len(text), 4000):
            await message.answer(text[i:i+4000])
        return

    unread = await db.get_unread_messages_for_admin()
    if not unread:
        await message.answer("Нет новых сообщений в поддержке.")
        return

    from keyboards import get_admin_support_keyboard
    for msg in unread:
        msg_id, user_id, text, photo_id = msg
        admin_text = f"Непрочитанное (Анонимный ID: {msg_id}):\n\n{text}"
        if photo_id:
            await message.answer_photo(photo=photo_id, caption=admin_text, reply_markup=get_admin_support_keyboard(msg_id))
        else:
            await message.answer(text=admin_text, reply_markup=get_admin_support_keyboard(msg_id))

@router.callback_query(F.data.startswith("admin_reply_support:"))
async def process_admin_reply_support(callback: CallbackQuery, state: FSMContext):
    msg_id = int(callback.data.split(":")[1])
    await state.set_state(AdminSupportStates.waiting_for_reply)
    await state.update_data(reply_to_msg_id=msg_id)
    await callback.message.answer(f"Напишите ответ на сообщение {msg_id}:")
    await callback.answer()

@router.message(AdminSupportStates.waiting_for_reply)
async def send_admin_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data['reply_to_msg_id']
    text = message.text
    
    user_id = await db.get_anonymous_id(msg_id)
    if not user_id:
        await message.answer("Ошибка: пользователь не найден.")
        await state.clear()
        return

    await db.save_admin_reply(user_id, text, msg_id)
    await db.mark_messages_as_read(msg_id)
    
    try:
        await message.bot.send_message(user_id, f"Сообщение от поддержки:\n\n{text}")
        await message.answer("Ответ успешно отправлен.")
        log_action(f"Admin replied to support msg {msg_id}")
    except Exception as e:
        await message.answer(f"Ошибка при отправке: {e}")
        
    await state.clear()
