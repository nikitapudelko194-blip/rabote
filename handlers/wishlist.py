from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from states import NavigationStates
from keyboards import get_navigation_keyboard
from database import Database

router = Router()
db = Database()

@router.message(F.text == "Вишлист")
async def show_wishlist(message: Message, state: FSMContext):
    wishlist = await db.get_all_wishlist()
    if not wishlist:
        await message.answer("Пока нет товаров в вишлисте.")
        return

    await state.set_state(NavigationStates.wishlist_navigation)
    await state.update_data(items=wishlist, current_index=0)
    
    item = wishlist[0]
    await message.answer_photo(photo=item[0], caption=item[1], reply_markup=get_navigation_keyboard("wishlist"))

@router.callback_query(F.data.startswith("wishlist_"), NavigationStates.wishlist_navigation)
async def process_wishlist_navigation(callback: CallbackQuery, state: FSMContext):
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
    
    await callback.message.edit_media(
        media=InputMediaPhoto(media=item[0], caption=item[1]),
        reply_markup=get_navigation_keyboard("wishlist")
    )
    await callback.answer()
