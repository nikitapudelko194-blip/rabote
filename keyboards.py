from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отзывы"), KeyboardButton(text="Предпоказ")],
            [KeyboardButton(text="Вишлист"), KeyboardButton(text="Донат")],
            [KeyboardButton(text="⭐ Избранное"), KeyboardButton(text="💬 Поддержка")],
            [KeyboardButton(text="👥 Рефералы")]
        ],
        resize_keyboard=True
    )

def get_admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить отзыв", callback_data="admin_add_review")],
            [InlineKeyboardButton(text="Добавить в Предпоказ", callback_data="admin_add_preview"),
             InlineKeyboardButton(text="Удалить из Предпоказа", callback_data="admin_del_preview")],
            [InlineKeyboardButton(text="Добавить в Вишлист", callback_data="admin_add_wishlist"),
             InlineKeyboardButton(text="Удалить из Вишлиста", callback_data="admin_del_wishlist")]
        ]
    )

def get_navigation_keyboard(prefix: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀ Назад", callback_data=f"{prefix}_prev"),
                InlineKeyboardButton(text="В меню", callback_data=f"{prefix}_menu"),
                InlineKeyboardButton(text="Вперед ▶", callback_data=f"{prefix}_next")
            ]
        ]
    )

def get_favorite_button(item_type, item_id, is_favorite):
    text = "💔 Удалить из избранного" if is_favorite else "❤️ В избранное"
    callback_data = f"{'remove' if is_favorite else 'add'}_fav:{item_type}:{item_id}"
    return InlineKeyboardButton(text=text, callback_data=callback_data)

def get_navigation_keyboard_with_fav(prefix: str, item_type: str, item_id: int, is_favorite: bool):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [get_favorite_button(item_type, item_id, is_favorite)],
            [
                InlineKeyboardButton(text="◀ Назад", callback_data=f"{prefix}_prev"),
                InlineKeyboardButton(text="В меню", callback_data=f"{prefix}_menu"),
                InlineKeyboardButton(text="Вперед ▶", callback_data=f"{prefix}_next")
            ]
        ]
    )

def get_favorites_navigation_keyboard(item_type, item_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💔 Удалить из избранного", callback_data=f"remove_fav_list:{item_type}:{item_id}")],
            [
                InlineKeyboardButton(text="◀ Назад", callback_data="fav_prev"),
                InlineKeyboardButton(text="В меню", callback_data="fav_menu"),
                InlineKeyboardButton(text="Вперед ▶", callback_data="fav_next")
            ]
        ]
    )

def get_admin_support_keyboard(msg_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Ответить", callback_data=f"admin_reply_support:{msg_id}")]]
    )
