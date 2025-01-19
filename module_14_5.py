from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from text import *
from keyboards import *
from crud_functions import *
import asyncio

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

initiate_db()
products = get_all_products()


@dp.message_handler(commands=['start'])
async def start(message):
    with open("files\start.png", "rb") as img:
        await message.answer_photo(img, f'Привет! {message.from_user.username}', reply_markup=kb)



@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию', reply_markup=ik)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])
    calories = int(10 * weight + 6.25 * growth - 5 * age + 5)
    await message.answer(f'Ваша норма калорий в день {calories}')
    await state.finish()

@dp.message_handler(text='Купить!')
async def get_buying_list(message):
    for product in products:
        id_, title, description, price = product
        img_path = f'files/{id_}.jpg'
        with open(f'{img_path}', 'rb') as img:
            await message.answer_photo(img, caption=f'Название: {title} | Описание: {description} | Цена: {price}p')
    await message.answer('Выберите продукт для покупки:', reply_markup=buy_products)

@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()



class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000

@dp.message_handler(text="Регистрация")
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    await state.update_data(username=message.text)
    data = await state.get_data()
    a = is_included(data['username'])
    if a is True:
        await state.update_data(username=message.text)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()
    else:
        await message.answer("Пользователь существует, введите другое имя")
        await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст: ")
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'])
    await message.answer("Пользователь успешно зарегистрирован!")
    await state.finish()


@dp.message_handler()
async def all_message(message):
    with open("files\message.png", "rb") as img:
        await message.answer_photo(img, 'Введите команду /start, чтобы начать общение.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
