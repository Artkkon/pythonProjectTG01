import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from config import TOKEN
from config import OPENWEATHERTOKEN

logging.basicConfig(level=logging.INFO)

API_TOKEN = TOKEN
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

OPENWEATHERMAP_API_KEY = OPENWEATHERTOKEN

@dp.message(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот, который может показать тебе прогноз погоды. Напиши название города.")

# Команда /help
@dp.message(commands=['help'])
async def send_help(message: types.Message):
    await message.answer("Просто напиши название города, и я пришлю тебе прогноз погоды.")

# Обработка текстовых сообщений
@dp.message()
async def get_weather(message: types.Message):
    city = message.text
    try:
        # Запрос к API OpenWeatherMap
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP

        data = response.json()

        # Проверка, что город найден
        if data.get("cod") != 200:
            raise ValueError(f"Город '{city}' не найден.")

        # Парсинг ответа
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        # Формирование ответа
        weather_info = (
            f"Погода в городе {city}:\n"
            f"Описание: {weather_description}\n"
            f"Температура: {temperature}°C\n"
            f"Влажность: {humidity}%\n"
            f"Скорость ветра: {wind_speed} м/с"
        )

        await message.answer(weather_info)

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к API: {e}")
        await message.answer("Произошла ошибка при подключении к сервису погоды. Попробуй позже.")

    except ValueError as e:
        logging.error(f"Ошибка: {e}")
        await message.answer(str(e))

    except KeyError as e:
        logging.error(f"Ошибка парсинга данных: {e}")
        await message.answer("Произошла ошибка при обработке данных. Попробуй еще раз.")

    except Exception as e:
        logging.error(f"Неизвестная ошибка: {e}")
        await message.answer("Произошла неизвестная ошибка. Попробуй снова.")

# Функция запуска бота
async def main():
    dp.include_router(dp)  # Подключаем роутер
    await bot.delete_webhook(drop_pending_updates=True)  # Удаление вебхуков (если были)
    await dp.start_polling(bot)  # Запуск поллинга

if __name__ == "__main__":
    asyncio.run(main())
