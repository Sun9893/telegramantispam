import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup,State
from datetime import timedelta
from aiogram import types
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,MessageToDeleteNotFound)
import asyncio
import os
from dotenv import load_dotenv
from contextlib import suppress

load_dotenv()

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w", format="%(asctime)s %(levelname)s %(message)s")
logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

bad_words = ['скамкал', 'ебырь', 'тувротс', 'спермкал', 'спидскана']

async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()

@dp.message_handler()
async def check_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    warnings_count = data.get('warnings', 1)
    for word in bad_words:
        if word in message.text.lower():
            msg = await message.reply(f"❌ Не используй бранные слова, в случае 3 предупреждений ты будешь заблокирован на 30 минут! \nНарушений {warnings_count}/3")
            asyncio.create_task(delete_message(msg, 5))

            if warnings_count >= 3:
                banned = await bot.send_message(message.chat.id, "❌ Ты заблокирован на 30 минут")
                asyncio.create_task(delete_message(banned, 5))
                new = types.ChatPermissions(can_send_messages=False)
                delta = timedelta(minutes=1)
                await bot.restrict_chat_member(chat_id=message.chat.id, user_id=user_id, permissions=new, until_date=delta)
                await state.update_data(warnings=1)
                return

            warnings_count += 1
            await state.update_data(warnings=warnings_count)
            await bot.delete_message(message.chat.id, message.message_id)
            return

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
