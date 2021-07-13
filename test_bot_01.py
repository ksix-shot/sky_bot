import config
import logging

from aiogram import Bot, Dispatcher, executor, types
from bd_conecter import SQLiter
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
#level logs
logging.basicConfig(level=logging.INFO)

#join to API
storage = MemoryStorage()
bot = Bot(token=config.bot_token)
dp = Dispatcher(bot,storage=storage)
db = SQLiter(database_file=config.db_name)


class Register_form(StatesGroup):
    name = State()
    inn = State()
    number = State()

@dp.message_handler(commands=['start'])
async def subsvribe(message: types.Message):
    if not db.user_exists(telegram_user_id=message.from_user.id):
        await bot.send_message(message.from_user.id, '''Добрый день меня зовут Bot Sky, вы у нас первый раз, 
    позвольте рассказать чем я могу быть полезен. У меня есть две задачи: 
        -рассказывать о новостях связанных с 1С
        -формировать заявки для моих друзей консультантов, которые будут вам помогать
    Для того что бы начать позвольте задать вам ряд вопросов''')
        await bot.send_message(message.from_user.id, "Как я могу к вам обращаться?")
        await Register_form.name.set()


@dp.message_handler(state=Register_form.name)
async def get_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer('Инн юр лица')

    await Register_form.next()

@dp.message_handler(state=Register_form.inn)
async def get_inn(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['inn'] = message.text

    await message.answer("Укажите ваш номер по которому можно будет с вами связаться")

    await Register_form.next()

@dp.message_handler(state=Register_form.number)
async def get_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number'] = message.text
    await message.answer("Спасибо что ответили на мои вопросы")

    db.add_user(telegram_user_id=message.from_user.id, name=data['name'],
                    phone=data['number'], inn=data['inn'], status=True)

    await state.finish()














if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)