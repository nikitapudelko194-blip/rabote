from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database import Database
from config import ADMIN_ID

router = Router()
db = Database()

router.message.filter(F.from_user.id == ADMIN_ID)

@router.message(Command("referral_stats"))
async def cmd_referral_stats(message: Message):
    top = await db.get_top_referrers()
    if not top:
        await message.answer("Рефералов пока нет.")
        return
        
    text = "Топ-10 рефоводов:\n\n"
    for idx, (name, count) in enumerate(top, 1):
        text += f"{idx}. {name} — {count} чел.\n"
        
    await message.answer(text)
