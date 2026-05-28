from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from states import NavigationStates
from keyboards import get_navigation_keyboard_with_fav
from database import Database

router = Router()
db = Database()

@router.message(F.text == "Предпоказ")
async def show_preview(message: Message, state: FSMContext):
    previews = await db.get_all_preview_with_id()
    if not previews:
        await message.answer("Пока нет товаров в предпоказе.")
        return

    await state.set_state(NavigationStates.preview_navigation)
    await state.update_data(items=previews, current_index=0)
    
    item = previews[0]
    item_id, photo_file_id, _ = item
    is_fav = await db.is_favorite(message.from_user.id, "preview", item_id)
    
    await message.answer_photo(photo=photo_file_id, reply_markup=get_navigation_keyboard_with_fav("preview", "preview", item_id, is_fav))

@router.callback_query(F.data == "cat_preview")
async def cb_show_preview(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    previews = await db.get_all_preview_with_id()
    if not previews:
        await callback.message.answer("Пока нет товаров в предпоказе.")
        return

    await state.set_state(NavigationStates.preview_navigation)
    await state.update_data(items=previews, current_index=0)
    
    item = previews[0]
    item_id, photo_file_id, _ = item
    is_fav = await db.is_favorite(callback.from_user.id, "preview", item_id)
    
    await callback.message.answer_photo(photo=photo_file_id, reply_markup=get_navigation_keyboard_with_fav("preview", "preview", item_id, is_fav))

@router.callback_query(F.data.startswith("preview_"), NavigationStates.preview_navigation)
async def process_preview_navigation(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    data = await state.get_data()
    items = data.get("items", [])
    current_index = data.get("current_index", 0)

    if action == "menu":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer("Вы вернулись в меню.")
        return

    if action == "next":
        if current_index + 1 < len(items):
            current_index += 1
        else:
            await callback.answer("Это последний товар", show_alert=True)
            return
    elif action == "prev":
        if current_index - 1 >= 0:
            current_index -= 1
        else:
            await callback.answer("Это первый товар", show_alert=True)
            return

    await state.update_data(current_index=current_index)
    item = items[current_index]
    item_id, photo_file_id, _ = item
    is_fav = await db.is_favorite(callback.from_user.id, "preview", item_id)
    
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo_file_id),
        reply_markup=get_navigation_keyboard_with_fav("preview", "preview", item_id, is_fav)
    )
    await callback.answer()
