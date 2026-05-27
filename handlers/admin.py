from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from keyboards import get_admin_menu
from states import AdminStates
from database import Database
from utils.logger import log_action

router = Router()
db = Database()

# Ограничиваем доступ только для администратора
router.message.filter(F.from_user.id == ADMIN_ID)
router.callback_query.filter(F.from_user.id == ADMIN_ID)

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    await message.answer("Панель администратора:", reply_markup=get_admin_menu())

# --- Добавить отзыв ---
@router.callback_query(F.data == "admin_add_review")
async def admin_add_review(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_review_text)
    await callback.message.answer("Отправьте текст отзыва:")
    await callback.answer()

@router.message(AdminStates.waiting_for_review_text, F.text)
async def process_review_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(AdminStates.waiting_for_review_photo)
    await message.answer("Отправьте фото для отзыва:")

@router.message(AdminStates.waiting_for_review_photo, F.photo)
async def process_review_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id
    await db.add_review(data['text'], photo_id)
    log_action("Админ добавил новый отзыв")
    await state.clear()
    await message.answer("Отзыв успешно добавлен!", reply_markup=get_admin_menu())

# --- Добавить в Предпоказ ---
@router.callback_query(F.data == "admin_add_preview")
async def admin_add_preview(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_preview_photo)
    await callback.message.answer("Отправьте фото для предпоказа:")
    await callback.answer()

@router.message(AdminStates.waiting_for_preview_photo, F.photo)
async def process_preview_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    max_idx = await db.get_max_order_index("preview")
    await db.add_preview(photo_id, max_idx + 1)
    log_action("Админ добавил товар в предпоказ")
    await state.clear()
    await message.answer("Добавлено в предпоказ!", reply_markup=get_admin_menu())

# --- Удалить из Предпоказа ---
@router.callback_query(F.data == "admin_del_preview")
async def admin_del_preview(callback: CallbackQuery, state: FSMContext):
    previews = await db.get_all_preview()
    if not previews:
        await callback.message.answer("Список предпоказа пуст.")
        return
    text = "Список для удаления (номер order_index):\n" + "\n".join([f"Индекс: {item[1]}" for item in previews])
    await callback.message.answer(text + "\nОтправьте номер (индекс) для удаления:")
    await state.set_state(AdminStates.waiting_for_delete_preview_id)
    await callback.answer()

@router.message(AdminStates.waiting_for_delete_preview_id, F.text)
async def process_del_preview(message: Message, state: FSMContext):
    try:
        idx = int(message.text)
        await db.delete_preview(idx)
        log_action(f"Админ удалил предпоказ с индексом {idx}")
        await message.answer(f"Предпоказ с индексом {idx} удален.", reply_markup=get_admin_menu())
    except ValueError:
        await message.answer("Пожалуйста, отправьте число.")
    finally:
        await state.clear()

# --- Добавить в Вишлист ---
@router.callback_query(F.data == "admin_add_wishlist")
async def admin_add_wishlist(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_wishlist_photo)
    await callback.message.answer("Отправьте фото для вишлиста:")
    await callback.answer()

@router.message(AdminStates.waiting_for_wishlist_photo, F.photo)
async def process_wishlist_photo(message: Message, state: FSMContext):
    await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(AdminStates.waiting_for_wishlist_caption)
    await message.answer("Отправьте описание (текст) для вишлиста:")

@router.message(AdminStates.waiting_for_wishlist_caption, F.text)
async def process_wishlist_caption(message: Message, state: FSMContext):
    data = await state.get_data()
    max_idx = await db.get_max_order_index("wishlist")
    await db.add_wishlist(data['photo_id'], message.text, max_idx + 1)
    log_action("Админ добавил товар в вишлист")
    await state.clear()
    await message.answer("Добавлено в вишлист!", reply_markup=get_admin_menu())

# --- Удалить из Вишлиста ---
@router.callback_query(F.data == "admin_del_wishlist")
async def admin_del_wishlist(callback: CallbackQuery, state: FSMContext):
    wishlist = await db.get_all_wishlist()
    if not wishlist:
        await callback.message.answer("Вишлист пуст.")
        return
    text = "Список для удаления (индекс - описание):\n" + "\n".join([f"{item[2]} - {item[1][:20]}..." for item in wishlist])
    await callback.message.answer(text + "\nОтправьте номер (индекс) для удаления:")
    await state.set_state(AdminStates.waiting_for_delete_wishlist_id)
    await callback.answer()

@router.message(AdminStates.waiting_for_delete_wishlist_id, F.text)
async def process_del_wishlist(message: Message, state: FSMContext):
    try:
        idx = int(message.text)
        await db.delete_wishlist(idx)
        log_action(f"Админ удалил товар из вишлиста с индексом {idx}")
        await message.answer(f"Элемент с индексом {idx} удален.", reply_markup=get_admin_menu())
    except ValueError:
        await message.answer("Пожалуйста, отправьте число.")
    finally:
        await state.clear()
