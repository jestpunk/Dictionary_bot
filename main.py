import telebot
from telebot import types

bot = telebot.TeleBot('6147352947:AAGw2dPTsNfXV501DMhsYXzrXlbkBucEU8o')

@bot.message_handler(commands=['start'])
def start_message(message):
    
    bot.send_message(message.from_user.id,
    f'Здравствуйте!, *{message.from_user.username}*!\n\n' +
    'Я — бот-словарь, созданный для хранения всех ваших слов и их переводов.\n\n' + 
    'Я отлично подхожу как для архивирования необычных слов на родном языке, так и ' + 
    'для изучения нового языка и накопления своего личного лексикона. Приступим?\n\n' + 
    '—'*30 + '\n\n' + '`[>] Для начала создайте словарь с помощью\n    кнопки "Создать словарь"`',
    parse_mode='Markdown'
    )

bot.polling(none_stop=True, interval=0)