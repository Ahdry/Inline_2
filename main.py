from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import filters
from aiogram.dispatcher.filters import Command, Text
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    age = State()
    height = State()
    weight = State()


API_TOKEN = ''  # Замените на ваш токен
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Создание клавиатуры
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = types.KeyboardButton('Рассчитать')
button_info = types.KeyboardButton('Информация')
keyboard.add(button_calculate, button_info)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью.")


@dp.message_handler(filters.Text(equals='Рассчитать'))
async def main_menu(message: types.Message):
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
    button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
    markup.add(button1, button2)
    await message.answer("Выберите опцию:", reply_markup=markup)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    formulas_message = (
        "Формула Миффлина-Сан Жеора:\n"
        "Для мужчин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5\n"
        "Для женщин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161"
    )
    await call.message.answer(formulas_message)
    await call.answer()  # Убираем загрузку кнопки


@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await Form.age.set()
    await call.message.answer("Пожалуйста, введите ваш возраст:")
    await call.answer()  # Убираем загрузку кнопки


@dp.message_handler(state=Form.age)
async def process_age(message: types.Message, state
: FSMContext):
    await state.update_data(age=message.text)
    await Form.height.set()
    await message.answer("Введите свой рост:")


@dp.message_handler(state=Form.height)
async def process_height(message: types.Message, state: FSMContext):
    await state.update_data(height=message.text)
    await Form.weight.set()
    await message.answer("Введите свой вес:")


@dp.message_handler(state=Form.weight)
async def process_weight(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    age = float(user_data['age'])
    height = float(user_data['height'])
    weight = float(message.text)

    # Расчет нормы калорий (пример для мужчины)
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
    await message.answer(f"Ваша норма калорий: {bmr:.2f} ккал.")

    await state.finish()  # Завершение состояния


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
