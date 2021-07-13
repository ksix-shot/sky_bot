from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class Register(StatesGroup):
    waiting_for_name = State()
    waiting_for_inn = State()
    waiting_for_number = State()
    waiting_for_status = State()

async def register_start(message: types.Message):
    await message.answer("Как я могу к вам обращаться?")
    await Register.waiting_for_name.set()

async def remember_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await Register.next()
    await message.answer("Напишите пожалуйста ИНН вашей организации, от имени которой будете обращаться")

async def remember_inn(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
