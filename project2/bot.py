import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import setup_handlers
from aiogram.types import BotCommand

bot = Bot(token=TOKEN)
dp = Dispatcher()

setup_handlers(dp)

async def main():
    print("Run bot")

    await bot.set_my_commands([
        BotCommand(command="start", description="Начать работу или получить информацию о боте"),
        BotCommand(command="help", description="Получить список доступных команд"),
        BotCommand(command="cancel", description="Отменить команду"),
        BotCommand(command="set_profile", description="Обновить профиль пользователя"),
        BotCommand(command="user_info", description="Получить данные пользователя"),
        BotCommand(command="log_water", description="Записать потребление воды"),
        BotCommand(command="log_food", description="Записать потребление пищи"),
        BotCommand(command="log_workout", description="Записать тренировку"),
        BotCommand(command="check_progress", description="Проверить показатели")
    ])

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
