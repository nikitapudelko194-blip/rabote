from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import StartState
from keyboards import get_main_menu
from database import Database

router = Router()
db = Database()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Добро пожаловать! Как к вам обращаться?")
        await state.set_state(StartState.waiting_for_name)
    else:
        await message.answer(f"С возвращением, {user[1]}!", reply_markup=get_main_menu())

@router.message(StartState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text
    await db.add_user(message.from_user.id, name)
    await state.clear()
    await message.answer(f"Приятно познакомиться, {name}!", reply_markup=get_main_menu())
