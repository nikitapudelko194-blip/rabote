from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from states import FavoritesStates
from keyboards import get_favorites_navigation_keyboard, get_navigation_keyboard_with_fav
from database import Database

router = Router()
db = Database()

@router.message(F.text == "⭐ Избранное")
async def show_favorites(message: Message, state: FSMContext):
    count = await db.count_user_favorites(message.from_user.id)
    if count == 0:
        await message.answer("Ваше избранное пока пусто.")
        return

    favorites = await db.get_user_favorites(message.from_user.id, limit=999, offset=0)
    await state.set_state(FavoritesStates.favorites_navigation)
    await state.update_data(items=favorites, current_index=0)
    
    await render_favorite_item(message, favorites[0], 0, count)

async def render_favorite_item(message_or_call, item, index, total):
    item_type, item_id = item
    if item_type == 'preview':
        data = await db.get_preview_by_id(item_id)
        if not data:
            return
        photo_file_id = data[0]
        caption = f"Избранное {index+1}/{total} (Предпоказ)"
    else:
        data = await db.get_wishlist_by_id(item_id)
        if not data:
            return
        photo_file_id, cap = data
        caption = f"Избранное {index+1}/{total} (Вишлист)\n\n{cap}"

    keyboard = get_favorites_navigation_keyboard(item_type, item_id)

    if isinstance(message_or_call, Message):
        await message_or_call.answer_photo(photo=photo_file_id, caption=caption, reply_markup=keyboard)
    else:
        await message_or_call.message.edit_media(
            media=InputMediaPhoto(media=photo_file_id, caption=caption),
            reply_markup=keyboard
        )

@router.callback_query(F.data.startswith("fav_"), FavoritesStates.favorites_navigation)
async def process_fav_navigation(callback: CallbackQuery, state: FSMContext):
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
    await render_favorite_item(callback, items[current_index], current_index, len(items))
    await callback.answer()

@router.callback_query(F.data.startswith("remove_fav_list:"))
async def remove_fav_list(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    item_type, item_id = parts[1], int(parts[2])
    await db.remove_favorite(callback.from_user.id, item_type, item_id)
    await callback.answer("Удалено из избранного", show_alert=True)
    
    favorites = await db.get_user_favorites(callback.from_user.id, limit=999, offset=0)
    if not favorites:
        await state.clear()
        await callback.message.delete()
        await callback.message.answer("Ваше избранное пусто.")
        return

    data = await state.get_data()
    current_index = data.get("current_index", 0)
    if current_index >= len(favorites):
        current_index = max(0, len(favorites) - 1)
        
    await state.update_data(items=favorites, current_index=current_index)
    await render_favorite_item(callback, favorites[current_index], current_index, len(favorites))

@router.callback_query(F.data.startswith("add_fav:"))
async def process_add_fav(callback: CallbackQuery):
    parts = callback.data.split(":")
    item_type, item_id = parts[1], int(parts[2])
    await db.add_favorite(callback.from_user.id, item_type, item_id)
    await callback.answer("Добавлено в избранное!", show_alert=True)
    prefix = "preview" if item_type == "preview" else "wishlist"
    await callback.message.edit_reply_markup(reply_markup=get_navigation_keyboard_with_fav(prefix, item_type, item_id, True))

@router.callback_query(F.data.startswith("remove_fav:"))
async def process_remove_fav(callback: CallbackQuery):
    parts = callback.data.split(":")
    item_type, item_id = parts[1], int(parts[2])
    await db.remove_favorite(callback.from_user.id, item_type, item_id)
    await callback.answer("Удалено из избранного!", show_alert=True)
    prefix = "preview" if item_type == "preview" else "wishlist"
    await callback.message.edit_reply_markup(reply_markup=get_navigation_keyboard_with_fav(prefix, item_type, item_id, False))
