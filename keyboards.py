from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отзывы"), KeyboardButton(text="Предпоказ")],
            [KeyboardButton(text="Вишлист"), KeyboardButton(text="Донат")]
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
