import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logging.getLogger('aiogram.event').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            user = event.from_user
            logger.info(
                f"Message | User: {user.id} ({user.username}) | "
                f"Text: {event.text} | Chat: {event.chat.id}"
            )
        return await handler(event, data)
