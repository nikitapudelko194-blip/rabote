import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import Database

# Импорт всех обработчиков
from handlers import start, menu, preview, wishlist, donate, reviews, admin

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Инициализация БД
    db = Database()
    await db.create_tables()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(preview.router)
    dp.include_router(wishlist.router)
    dp.include_router(donate.router)
    dp.include_router(reviews.router)
    dp.include_router(admin.router)

    from handlers import favorites, support, admin_support, referral, admin_referral
    dp.include_router(favorites.router)
    dp.include_router(support.router)
    dp.include_router(admin_support.router)
    dp.include_router(referral.router)
    dp.include_router(admin_referral.router)

    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="Перезапуск бота"),
        BotCommand(command="support", description="💬 Поддержка")
    ])

    try:
        print("Бот успешно запущен!")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
