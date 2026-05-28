from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import StartState
from keyboards import get_main_menu
from database import Database

router = Router()
db = Database()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    user = await db.get_user(message.from_user.id)
    args = command.args
    
    if not user:
        if args and args.startswith("REF"):
            await state.update_data(referred_by=args)
            
        await message.answer("Добро пожаловать! Как к вам обращаться?")
        await state.set_state(StartState.waiting_for_name)
    else:
        await message.answer(f"С возвращением, {user[1]}!", reply_markup=get_main_menu())

@router.message(StartState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    ref_code = data.get("referred_by")
    
    await db.add_user(user_id, name)
    
    if ref_code:
        referrer_id = await db.validate_referral_code(ref_code)
        if referrer_id and referrer_id != user_id:
            is_ref = await db.is_already_referred(user_id)
            if not is_ref:
                await db.save_referral(referrer_id, user_id)
                await db.add_bonus(referrer_id, 1, 'signup')
                try:
                    await message.bot.send_message(referrer_id, f"🎉 По вашей ссылке зарегистрировался новый пользователь! Вам начислен +1 бонус.")
                except Exception:
                    pass

    await state.clear()
    await message.answer(f"Приятно познакомиться, {name}!", reply_markup=get_main_menu())
