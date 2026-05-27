from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_review_text = State()
    waiting_for_review_photo = State()
    waiting_for_preview_photo = State()
    waiting_for_delete_preview_id = State()
    waiting_for_wishlist_photo = State()
    waiting_for_wishlist_caption = State()
    waiting_for_delete_wishlist_id = State()

class NavigationStates(StatesGroup):
    preview_navigation = State()
    wishlist_navigation = State()
    reviews_navigation = State()

class StartState(StatesGroup):
    waiting_for_name = State()
