from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards import get_main_menu, get_inline_categories_menu

router = Router()

@router.message(F.text == "В меню")
async def go_to_menu(message: Message):
    await message.answer("Вы вернулись в главное меню", reply_markup=get_main_menu())

@router.message(F.text == "📂 Категории")
async def show_categories(message: Message):
    await message.answer("Выберите нужную категорию:", reply_markup=get_inline_categories_menu())

@router.callback_query(F.data == "cat_main_menu")
async def process_cat_main_menu(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Вы вернулись в главное меню.", reply_markup=get_main_menu())
    await callback.answer()

@router.callback_query(F.data == "cat_restart")
async def process_cat_restart(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Бот перезапущен. Добро пожаловать!", reply_markup=get_main_menu())
    await callback.answer()
