from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from states import NavigationStates
from keyboards import get_navigation_keyboard
from database import Database

router = Router()
db = Database()

@router.message(F.text == "Отзывы")
async def show_reviews(message: Message, state: FSMContext):
    reviews = await db.get_all_reviews()
    if not reviews:
        await message.answer("Пока нет отзывов.")
        return

    await state.set_state(NavigationStates.reviews_navigation)
    await state.update_data(items=reviews, current_index=0)
    
    item = reviews[0]
    text, photo_file_id = item
    await message.answer_photo(photo=photo_file_id, caption=text, reply_markup=get_navigation_keyboard("reviews"))

@router.callback_query(F.data.startswith("reviews_"), NavigationStates.reviews_navigation)
async def process_reviews_navigation(callback: CallbackQuery, state: FSMContext):
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
            await callback.answer("Это последний отзыв", show_alert=True)
            return
    elif action == "prev":
        if current_index - 1 >= 0:
            current_index -= 1
        else:
            await callback.answer("Это первый отзыв", show_alert=True)
            return

    await state.update_data(current_index=current_index)
    item = items[current_index]
    text, photo_file_id = item
    
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo_file_id, caption=text),
        reply_markup=get_navigation_keyboard("reviews")
    )
    await callback.answer()
