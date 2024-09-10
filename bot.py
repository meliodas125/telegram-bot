import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import F
import asyncio
from datetime import datetime

# Включаем логирование
logging.basicConfig(level=logging.INFO)

API_TOKEN = '7508024324:AAGiDcLGzGzZufvyB5efVqkT3FFEBAOfRGs'

# Инициализация бота
bot = Bot(token=API_TOKEN, session=AiohttpSession())
dp = Dispatcher()

# Хранилище для данных
data = {}
sleep_start = None  # Время начала сна

# Создание кнопок для главного меню
keyboard_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Кормление')],
        [KeyboardButton(text='Сон начался')],
        [KeyboardButton(text='Сон закончился')],
        [KeyboardButton(text='Ежедневный отчет')],
        [KeyboardButton(text='Еженедельный отчет')]
    ],
    resize_keyboard=True
)


# Стартовое сообщение с клавиатурой
@dp.message(F.text == "/start")
async def send_welcome(message: types.Message):
    await message.answer("Привет! Вот ваши кнопки для записи данных и отчетов.", reply_markup=keyboard_main)


# Обработчик кнопки "Кормление"
@dp.message(F.text == 'Кормление')
async def ask_feed_amount(message: types.Message):
    await message.answer("Введите количество выпитого молока в миллилитрах:")


# Запись данных о кормлении
@dp.message(lambda message: message.text.isdigit())
async def record_feed(message: types.Message):
    amount = int(message.text)
    today = datetime.now().strftime('%Y-%m-%d')
    if today not in data:
        data[today] = {'milk': 0, 'sleep': []}
    data[today]['milk'] += amount
    await message.answer(f"Записано: {amount} мл молока.")


# Обработчик кнопки "Сон начался"
@dp.message(F.text == 'Сон начался')
async def start_sleep(message: types.Message):
    global sleep_start
    sleep_start = datetime.now().strftime('%H:%M')
    await message.answer(f"Сон начался в {sleep_start}.")


# Обработчик кнопки "Сон закончился"
@dp.message(F.text == 'Сон закончился')
async def end_sleep(message: types.Message):
    global sleep_start
    if sleep_start:
        sleep_end = datetime.now().strftime('%H:%M')
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in data:
            data[today] = {'milk': 0, 'sleep': []}
        data[today]['sleep'].append(f"{sleep_start}-{sleep_end}")
        await message.answer(f"Сон завершен. Записано время сна: {sleep_start}-{sleep_end}.")
        sleep_start = None
    else:
        await message.answer("Время начала сна не было записано. Нажмите 'Сон начался'.")


# Обработчик кнопки "Ежедневный отчет"
@dp.message(F.text == 'Ежедневный отчет')
async def daily_report(message: types.Message):
    today = datetime.now().strftime('%Y-%m-%d')
    if today in data:
        milk = data[today]['milk']
        sleep_times = ', '.join(data[today]['sleep'])
        await message.answer(f"Сегодня выпито {milk} мл молока.\nМирон спал в эти часы: {sleep_times}")
    else:
        await message.answer("Данных за сегодня нет.")


# Обработчик кнопки "Еженедельный отчет"
@dp.message(F.text == 'Еженедельный отчет')
async def weekly_report(message: types.Message):
    report = []
    total_milk = 0
    previous_day_milk = 0
    increasing = True

    for day, stats in data.items():
        milk = stats['milk']
        sleep_times = ', '.join(stats['sleep'])
        report.append(f"{day}: выпито {milk} мл, сон: {sleep_times}")
        total_milk += milk

        if previous_day_milk and milk < previous_day_milk:
            increasing = False
        previous_day_milk = milk

    report.append(f"Общее количество молока за неделю: {total_milk} мл.")
    if increasing:
        report.append("Потребление молока увеличилось.")
    else:
        report.append("Потребление молока не увеличилось.")

    await message.answer("\n".join(report))


# Запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # Удаляем вебхуки и старые обновления
    await dp.start_polling(bot)  # Запускаем поллинг для получения сообщений


if __name__ == '__main__':
    asyncio.run(main())
