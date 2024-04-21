import telebot
from telebot import types
import requests
import json
from currency_converter import CurrencyConverter

bot = telebot.TeleBot('7083039146:AAELYaL2vdiG9HOwdAe5yK1tSuGudhvHZ0E')
API_KEY = '17d63c489fafe79d7423a89e7bf4f443'
currency = CurrencyConverter()
#API ПОГОДЫ - https://openweathermap.org/
amount = 0



@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_converter = types.KeyboardButton('Конвертер')
    btn_weather = types.KeyboardButton('Узнать погоду')
    btn_end = types.KeyboardButton('Закончить работу')
    markup.row(btn_converter, btn_weather)
    markup.row(btn_end)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}', reply_markup=markup)
    bot.register_next_step_handler(message, click_on)






def click_on(message):
    if message.text == 'Узнать погоду':
        bot.send_message(message.chat.id, 'Хорошо, напиши название города')
        bot.register_next_step_handler(message, get_weather)
    elif message.text == 'Конвертер':
        bot.send_message(message.chat.id, 'Хорошо введи сумму которую нужено перевести')
        bot.register_next_step_handler(message, get_currency)


def get_weather(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        weather = data['weather'][0]['main']
        temp = data['main']['temp']
        if weather.lower() == 'clouds':
            bot.reply_to(message, f'Cейчас: 🌥🌥🌥 {weather} {temp} °C')
        elif weather.lower() == 'clear' or weather.lower() == 'sunny':
            bot.reply_to(message, f'Cейчас: ☀️☀️☀️ {weather} {temp} °C')
        elif weather.lower() == 'rain' or weather.lower() == 'drizzle':
            bot.reply_to(message, f'Cейчас: ☔️☔️☔️ {weather} {temp} °C')
        elif weather.lower() == 'snow':
            bot.reply_to(message, f'Cейчас: 🌨🌨🌨 {weather} {temp} °C')
        bot.send_message(message.chat.id, 'Погоду в каком городе хотел бы еще узнать?')
        bot.register_next_step_handler(message, get_weather)
    else:
        bot.send_message(message.chat.id, 'Неверный указан город, введите заново')
        bot.register_next_step_handler(message, get_weather)
        return

def get_currency(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ты ввел неверные данные, давай попробуй снова😉')
        bot.register_next_step_handler(message, get_currency)
        return
    if amount > 0:
        mark_up = types.InlineKeyboardMarkup(row_width=2)
        btn_tjs_ru = types.InlineKeyboardButton('TJS/RU', callback_data='TJS/RU')
        btn_ru_tjs = types.InlineKeyboardButton('RU/TJS', callback_data='RU/TJS')
        btn_usd_tjs = types.InlineKeyboardButton('USD/TJS', callback_data='USD/TJS')
        btn_else = types.InlineKeyboardButton('другое значение', callback_data='else')
        mark_up.add(btn_tjs_ru, btn_ru_tjs, btn_usd_tjs,btn_else)
        bot.send_message(message.chat.id, 'Выбери пару валют', reply_markup=mark_up)
    else:
        bot.send_message(message.chat.id, 'Ты смеешься надо мной? как из пустоты мне тебе помочь😐? Давай попробуй заново')
        bot.register_next_step_handler(message, get_currency)
    return amount


@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    values = call.data.split('/')
    if len(values) > 1:
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f'Получатеся {res}')
    else:
        bot.send_message(call.message.chat.id, 'Введи первую валюту, например: USD')
        values.append(call.message.text.upper())
        bot.send_message(call.message.chat.id, f"{values}")


bot.polling(non_stop=True)