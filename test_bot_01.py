import config
import logging

from aiogram import Bot, Dispatcher, executor, types
from bd_conecter import SQLiter
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

# level logs
logging.basicConfig(level=logging.INFO)

# join to API
storage = MemoryStorage()
bot = Bot(token=config.bot_token)
dp = Dispatcher(bot, storage=storage)
db = SQLiter(database_file=config.db_name)


class Register_form(StatesGroup):
    name = State()
    inn = State()
    number = State()
    sub_news = State()

class CreateOrder(StatesGroup):
    programa = State()
    vopros = State()
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
    bool_keybord = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='ДА'), KeyboardButton(text='НЕТ')]],
        resize_keyboard=True

    )
    await message.answer("Хотели бы получать новости из мира 1С? Напишите ДА/НЕТ", reply_markup=bool_keybord)
    await Register_form.next()


@dp.message_handler(state=Register_form.sub_news)
async def get_sub(message: types.Message, state: FSMContext):
    #ТРЕБУЕТСЯ ДОРАБОТКА ПРИСВАИВАНИЕ ПЕРЕМЕННЫХ МЕДЛЕНИЕ ЧЕМ АСИНХРОННЫЙ ВЫЗОВ ФУНКЦИИ
    if message.text == 'ДА':
        async with state.proxy() as data:
            data["status"] = True
            db.add_user(telegram_user_id=message.from_user.id, name=data['name'],
                              phone=data['number'], inn=data['inn'], status=data["status"])
    elif message.text == 'НЕТ':
        async with state.proxy() as data:
            data["status"] = False
            db.add_user(telegram_user_id=message.from_user.id, name=data['name'],
                              phone=data['number'], inn=data['inn'], status=data["status"])

    #await db.add_user(telegram_user_id=message.from_user.id, name=data['name'],
            #phone=data['number'], inn=data['inn'], status=data["status"])
    await message.answer('Отлично, теперь я смогу формировать заявки и будете тратить меньше времени', reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(text='Заказать консультацию')
async def create_zaiavka(message: types.Message):
    if not db.user_exists(telegram_user_id=message.from_user.id):
        await bot.send_message(message.from_user.id, "Мы с вами еще не знакомы))) Для того что бы завести заявку нужно ввести /start")
    else:
        await bot.send_message(message.from_user.id, "По какой программе у вас вопрос?", reply_markup=ReplyKeyboardRemove())
        await CreateOrder.programa.set()


@dp.message_handler(state=CreateOrder.programa)
async def get_programma(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['programma'] = message.text
    await bot.send_message(message.from_user.id, "Какой у вас вопрос?")
    await CreateOrder.next()

@dp.message_handler(state=CreateOrder.vopros)
async def get_vopros(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vopros'] = message.text

    number = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=db.user_info(telegram_user_id=message.from_user.id)[4])]],
        resize_keyboard=True
    )
    await bot.send_message(message.from_user.id,
                           "По какому номеру можно будет с вами связаться?, можете выбрать тот номер который указали при регистрации либо ввести другой уже с помощью клавиатуры",
                           reply_markup=number)
    await CreateOrder.next()

@dp.message_handler(state=CreateOrder.number)
async def get_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number'] = message.text
    user_info = db.user_info(message.from_user.id)
    parse = f'''Инн {user_info[3]}
Имя {user_info[2]}
Программа {data['programma']}
Вопрос {data['vopros']}
Номер для связи {data['number']}'''
    await bot.send_message(chat_id=config.chat_conc, text=parse)
    await message.answer( "Ваша заявка зарегистрирована", reply_markup=ReplyKeyboardRemove())
    await state.finish()

@dp.message_handler(commands='menu')
async def show_menu(message: types.Message):
    number = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("Заказать консультацию")]],
        resize_keyboard=True

    )
    await bot.send_message(message.from_user.id, 'Выберете команду', reply_markup=number)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
