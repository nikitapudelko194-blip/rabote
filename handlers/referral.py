from aiogram import Router, F
from aiogram.types import Message
from database import Database

router = Router()
db = Database()

@router.message(F.text == "👥 Рефералы")
async def show_referrals(message: Message):
    user_id = message.from_user.id
    
    code = await db.get_referral_code(user_id)
    if not code:
        import string
        import random
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code = f"REF{user_id}_{random_str}"
        await db.generate_referral_code(user_id, code)
        
    bot_user = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_user.username}?start={code}"
    
    count = await db.get_referral_count(user_id)
    balance = await db.get_bonus_balance(user_id)
    recent = await db.get_recent_referrals(user_id)
    
    text = f"Ваша реферальная ссылка:\n`{ref_link}`\n\n"
    text += f"Приглашено: {count} чел.\n"
    text += f"Ваш баланс: {balance} бонусов\n\n"
    
    if recent:
        text += "Последние 5 приглашенных:\n"
        for created_at, name in recent:
            text += f"- {name} ({created_at[:10]})\n"
            
    await message.answer(text, parse_mode="Markdown")
