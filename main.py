import telebot
from telebot import types
from collections import defaultdict as dd
import enum
import os
from dotenv import load_dotenv

class ResultCodes(enum.Enum):
    '''
    Enum класс для упорядочивания
    кодов, возвращаемых функциями
    '''

    ok = 0
    word_already_exist = 1

class Dictionary:
    '''
    Класс словаря, хранящего слова и их переводы

    self.name: str — имя словаря
    self.mapping: defaultdict — словарь типа "слово: перевод"
    '''

    def __init__(self, name: str):
        self.name = name
        self.mapping = dd(str)


    def __str__(self) -> str:
        res = f'`{self.name}`\n\n'
        if len(self.mapping.keys()) > 0:
            sorted_keys = sorted(self.mapping.keys())
            for k in sorted_keys:
                v = self.mapping[k]
                res += f'\t`{k}` —— '
                res += str(v[:15])
                res += ('...' if (len(v) > 15) else '')
                res += '\n'
        else:
            res += '\tЭтот словарь пуст...'
        return res + '\n'


    def get_name(self) -> str:
        if not hasattr(self, 'name'):
            raise ValueError('Dictionary do not have a name')
        return self.name


    def change_name(self, new_name: str) -> int:
        self.name = new_name
        return ResultCodes.ok.value


    def add_word(self, word: str, translation: str, forced=False) -> int:
        # Проверяем, существует ли слово в словаре
        if not forced and word in self.mapping.keys():
            return ResultCodes.word_already_exist.value
        
        # Добавляем слово
        self.mapping[word] = translation


load_dotenv()

# 'Итальянский': Dictionary('Итальянский', ...)
dictionaries = dd(str)
max_dict_name_len = 20
first = True


#bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
bot = telebot.TeleBot('6147352947:AAGw2dPTsNfXV501DMhsYXzrXlbkBucEU8o')

def update_dicts_markup():
    global dicts_markup

    dicts_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for d in dictionaries.values():
        dicts_markup.add(types.KeyboardButton(d.get_name()))

flags_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn_blank = types.KeyboardButton("❌")
btn_rus = types.KeyboardButton("🇷🇺")
btn_eng = types.KeyboardButton("🇬🇧")
btn_ger = types.KeyboardButton("🇩🇪")
btn_kor = types.KeyboardButton("🇰🇷")
btn_jap = types.KeyboardButton("🇯🇵")
btn_chi = types.KeyboardButton("🇨🇳")
btn_ita = types.KeyboardButton("🇮🇹")
btn_fra = types.KeyboardButton("🇫🇷")
btn_spa = types.KeyboardButton("🇪🇸")
flags_markup.add(btn_blank,
            btn_rus,
            btn_eng,
            btn_ger,
            btn_kor,
            btn_jap,
            btn_chi,
            btn_ita,
            btn_fra,
            btn_spa)

menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn_create_dict = types.KeyboardButton("Добавить словарь")
btn_create_word = types.KeyboardButton("Добавить слово")
btn_view_dicts = types.KeyboardButton("Список словарей")
btn_view_dict = types.KeyboardButton("Заглянуть в словарь")
btn_delete_dict = types.KeyboardButton("Удалить словарь")
btn_delete_word = types.KeyboardButton("Удалить слово")
menu_markup.add(btn_create_dict,
            btn_create_word,
            btn_view_dicts,
            btn_view_dict,
            btn_delete_dict,
            btn_delete_word)


# НАЧАЛО
@bot.message_handler(commands=['start'])
def start_message(message):
    global first
    
    if first:
        sent = bot.send_message(message.from_user.id,
        f'Здравствуйте!, *{message.from_user.username}*!\n\n' +
        'Я — бот-словарь, созданный для хранения всех ваших слов и их переводов.\n\n' + 
        'Я отлично подхожу как для архивирования необычных слов на родном языке, так и ' + 
        'для изучения нового языка и накопления своего личного лексикона. Приступим?\n\n' + 
        '—'*30 + '\n\n' + '`[>] Для начала создайте словарь с помощью\n' + ' ' * 4 + 'кнопки "Добавить словарь"`',
        parse_mode='Markdown',
        reply_markup=menu_markup
        )
        first = False
    else:
        sent = bot.send_message(message.from_user.id,
        f'Выберите опцию из предложенных ниже',
        parse_mode='Markdown',
        reply_markup=menu_markup
        )
        first = False

    bot.register_next_step_handler(sent, manager)


def manager(message):
    operation = message.text
    if operation == "Добавить словарь":
        add_dictionary(message)
    elif operation == "Список словарей":
        list_of_dictionaries(message)
    elif operation == "Заглянуть в словарь":
        look_to_dictionary(message)
    elif operation == 'Добавить слово':
        add_word(message)
    elif operation == 'Удалить словарь':
        delete_dict(message)
    elif operation == 'Удалить слово':
        delete_word(message)
    else:
        bot.send_message(message.from_user.id, 'Неизвестная команда!')
        start_message(message)




# УДАЛИТЬ СЛОВО
@bot.message_handler(commands=['delete_word'])
def delete_word(message):
    if len(dictionaries.keys()) == 0:
        bot.send_message(message.from_user.id,
        'К сожалению у вас пока нет словарей. Добавьте их с помощью кнопки "Добавить словарь"',
        parse_mode='Markdown')
        start_message(message)
        return
    
    update_dicts_markup()
    
    sent = bot.send_message(message.from_user.id, 'Выберите словарь из списка',
    reply_markup=dicts_markup)
    bot.register_next_step_handler(sent, have_dict_name_to_delete_word)


def have_dict_name_to_delete_word(message):
    dict_name = message.text
    if dict_name not in dictionaries.keys():
        bot.send_message(message.from_user.id, 'Такого словаря не существует!')
        delete_word(message)

    else:
        words = sorted(dictionaries[dict_name].mapping.keys())
        words_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for w in words:
            words_markup.add(types.KeyboardButton(w))
        
        sent = bot.send_message(message.from_user.id, 'Какое слово вы хотите удалить?',
        reply_markup=words_markup)
        bot.register_next_step_handler(sent, have_dict_name_and_word_to_delete, message, dict_name)


def have_dict_name_and_word_to_delete(message, old_message, dict_name):
    word = message.text
    if word not in dictionaries[dict_name].mapping.keys():
        bot.send_message(message.from_user.id, "Такого слова не существует!")
        have_dict_name_to_delete_word(old_message)

    else:
        dictionaries[dict_name].mapping.pop(word)
        bot.send_message(message.from_user.id, f"Слово {word} успешно удалено")
        start_message(message)


# УДАЛИТЬ СЛОВАРЬ
@bot.message_handler(commands=['delete_dict'])
def delete_dict(message):
    if len(dictionaries.keys()) == 0:
        bot.send_message(message.from_user.id,
        'К сожалению у вас пока нет словарей. Добавьте их с помощью кнопки "Добавить словарь"',
        parse_mode='Markdown')
        start_message(message)
        return
    
    update_dicts_markup()
    
    sent = bot.send_message(message.from_user.id, 'Выберите словарь из списка',
    reply_markup=dicts_markup)
    bot.register_next_step_handler(sent, have_dict_name_to_delete_dict) 


def have_dict_name_to_delete_dict(message):
    dict_name = message.text
    if dict_name not in dictionaries.keys():
        bot.send_message(message.from_user.id, 'Такого словаря не существует!')
        delete_dict(message)

    else:
        dictionaries.pop(dict_name)
        bot.send_message(message.from_user.id, f'Словарь {dict_name} успешно удалён!')
        start_message(message)


# ДОБАВИТЬ СЛОВО
@bot.message_handler(commands=['add_word'])
def add_word(message):
    if len(dictionaries.keys()) == 0:
        bot.send_message(message.from_user.id,
        'К сожалению у вас пока нет словарей. Добавьте их с помощью кнопки "Добавить словарь"',
        parse_mode='Markdown')
        start_message(message)
        return
    
    update_dicts_markup()
    
    sent = bot.send_message(message.from_user.id, 'Выберите словарь из списка',
    reply_markup=dicts_markup)

    bot.register_next_step_handler(sent, have_dict_name_to_add_word) 


def have_dict_name_to_add_word(message):
    dict_name = message.text
    if dict_name not in dictionaries.keys():
        bot.send_message(message.from_user.id, 'Такого словаря не существует!')
        add_word(message)

    else:
        sent = bot.send_message(message.from_user.id, 'Введите новое слово')
        bot.register_next_step_handler(sent, have_word_to_add, dict_name)


def have_word_to_add(message, dict_name, forced=False):
    word = message.text

    if not forced and word in dictionaries[dict_name].mapping.keys():

        yes_no_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_yes = types.KeyboardButton("Да")
        btn_no  = types.KeyboardButton("Нет")
        yes_no_markup.add(btn_yes, btn_no)
        sent = bot.send_message(message.from_user.id, f'Слово {word} уже присутствует в словаре! Хотите его поменять?',
        reply_markup=yes_no_markup)
        bot.register_next_step_handler(sent, word_overwrite, message, dict_name)

    else:
        sent = bot.send_message(message.from_user.id, f'Отлично! Теперь введите перевод слова {word}')
        bot.register_next_step_handler(sent, have_word_and_translation_to_add, dict_name, word)


def word_overwrite(message, old_message, dict_name):
    answer = message.text
    if answer == 'Да':
        have_word_to_add(old_message, dict_name, forced=True)
    else:
        start_message(message)


def have_word_and_translation_to_add(message, dict_name, word):
    translation = message.text
    dictionaries[dict_name].mapping[word] = translation
    bot.send_message(message.from_user.id, f'Слово {word} успешно добавлено в словарь {dict_name}')
    start_message(message)


# ЗАГЛЯНУТЬ В СЛОВАРЬ
@bot.message_handler(commands=['look_to_dictionary'])
def look_to_dictionary(message):
    global dicts_markup
    
    if len(dictionaries.keys()) == 0:
        bot.send_message(message.from_user.id,
        'К сожалению у вас пока нет словарей. Добавьте их с помощью кнопки "Добавить словарь"',
        parse_mode='Markdown')
        start_message(message)

    update_dicts_markup()
    
    sent = bot.send_message(message.from_user.id, 'Выберите словарь из списка',
    reply_markup=dicts_markup)

    bot.register_next_step_handler(sent, have_dict_name_to_watch) 
    

def have_dict_name_to_watch(message):
    dict_name = message.text
    if dict_name not in dictionaries.keys():
        bot.send_message(message.from_user.id, 'Такого словаря не существует!')
        look_to_dictionary(message)
    else:
        bot.send_message(message.from_user.id, f'{dictionaries[dict_name]}',
        parse_mode='Markdown')
        start_message(message)





# СПИСОК СЛОВАРЕЙ
@bot.message_handler(commands=['list_of_dictionaries'])
def list_of_dictionaries(message):
    bot.reply_to(message, 
    (f'*Ваши словари*:\n\n' + 
    parse_to_human_readable(dictionaries)),
    parse_mode='Markdown')
    
    start_message(message)


def parse_to_human_readable(dicts):
    if len(dicts.keys()) == 0:
        return 'тут пусто...'
    
    res = ''
    for k, v in dicts.items():
        res += (str(v) + '\n')
    return res   





# ДОБАВИТЬ СЛОВАРЬ
@bot.message_handler(commands=['add_dictionary'])
def add_dictionary(message):
    
    sent = bot.send_message(message.from_user.id, 'Давайте добавим для вас новый словарь!\n\n' + 
    'Для этого введите его имя\n\n' +
    f'`ВАЖНО! Длина имени не превысит {max_dict_name_len} символов`')
    bot.register_next_step_handler(sent, got_name)   


def got_name(message):
    name = message.text[:20]
    sent = message
    try:
        sent = bot.send_message(message.from_user.id, 
        f'Отлично, давай назовём словарь `{name}`!\n\nТеперь выбери эмодзи, ' +
        'которое будет выступать ярлыком словаря. Ты '+
        'можешь выбрать ❌, чтобы не добавлять эмодзи', 
        parse_mode='Markdown',
        reply_markup=flags_markup)
        bot.register_next_step_handler(sent, got_name_and_emoji, name)
    except:
        sent = bot.send_message(message.from_user.id, 'Недопустимое название. Попробуйте еще раз.')
        bot.register_next_step_handler(sent, got_name)


def got_name_and_emoji(message, name):
    global dictionaries
    
    emoji = message.text
    new_name = (name + ' ' + emoji) if (emoji != "❌") else name
    dictionaries[new_name] = Dictionary(new_name)
    
    sent = bot.send_message(message.from_user.id, 
    f'Готово! Новый словарь будет называться `{new_name}`!')
    
    start_message(message)


bot.polling(none_stop=True, interval=0)