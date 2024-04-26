import telebot
from telebot import types
import requests
import json
from currency_converter import CurrencyConverter

bot = telebot.TeleBot('7083039146:AAELYaL2vdiG9HOwdAe5yK1tSuGudhvHZ0E')
API_KEY = '17d63c489fafe79d7423a89e7bf4f443'
API_CURRENCY_KEY = '0c0d67ff38861fb004dba8bd'

currency = CurrencyConverter()
#API ПОГОДЫ - https://openweathermap.org/




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
    elif message.text == 'Закончить работу':
        bot.send_message(message.chat.id, 'Рад был тебе помочь😎, нужна будет еще помощь пиши /start и я тебе помогу')


def get_weather(message):
    city = message.text.strip()
    if city == 'закончить работу':
        bot.register_next_step_handler(message, click_on)
        return
    else:
        city = city.lower()
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
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ты ввел неверные данные, давай попробуй снова😉')
        bot.register_next_step_handler(message, get_currency)
        return
    amounts = {}
    amounts[str(message.chat.id)] = str(amount)
    with open('amount.json', 'w') as f:
        json.dump(amounts, f)

    if amount > 0:
        mark_up = types.InlineKeyboardMarkup(row_width=2)
        btn_usd_tjs = types.InlineKeyboardButton('USD/TJS', callback_data='USD/TJS')
        btn_tjs_usd = types.InlineKeyboardButton('TJS/USD', callback_data='TJS/USD')
        btn_else = types.InlineKeyboardButton('другое значение', callback_data='else')
        mark_up.add(btn_tjs_usd, btn_usd_tjs, btn_else)
        bot.send_message(message.chat.id, 'Выбери пару валют', reply_markup=mark_up)
    else:
        bot.send_message(message.chat.id, 'Ты смеешься надо мной? как из пустоты мне тебе помочь😐? Давай попробуй заново')
        bot.register_next_step_handler(message, get_currency)



@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'USD/TJS' or call.data == 'USD/TJS':
        message = call.message
        convert(message, call.data)
    elif call.data == 'else':
        markup = types.InlineKeyboardMarkup()
        btn_info = types.InlineKeyboardButton('Если ты не знаешь, тут я тебе помогу', callback_data='info')
        markup.add(btn_info)
        bot.send_message(call.message.chat.id, 'Введи абривиатуру валют через слэш, например "USD/EUR"',
                         reply_markup=markup)
        bot.register_next_step_handler(call.message, convert)

    elif call.data == 'info':
        res = requests.get(f'https://v6.exchangerate-api.com/v6/{API_CURRENCY_KEY}/codes')
        result = res.json()
        data = ['-'.join(item) for item in result["supported_codes"]]
        text_message = '\n'.join(data)
        print(text_message)
        bot.send_message(call.message.chat.id, f'{text_message}')
        bot.send_message(call.message.chat.id, 'Выбери то что тебе нужно и напиши валюты через слэш, например "USD/EUR ')
        bot.register_next_step_handler(call.message, convert)



def convert(message, currencies:str=None):
    if currencies is None:
        currencies = message.text.strip().upper()
    with open('amount.json', 'r') as f:
        amounts = json.load(f)
    amount = amounts[str(message.chat.id)]
    values = currencies
    response = requests.get(f'https://v6.exchangerate-api.com/v6/{API_CURRENCY_KEY}/pair/{values}/{amount}')
    values = values.split('/')
    data = json.loads(response.text)
    result = data['conversion_result']
    bot.send_message(message.chat.id, f'{amount} {values[0]} = {result} {values[1]}')






bot.polling(non_stop=True)