import telebot
from telebot import types
from collections import defaultdict as dd
import enum
from telebot.storage import StateMemoryStorage

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
        res = f'*{self.name}*\n\n'
        if len(self.mapping.keys() > 0):
            for k, v in self.mapping.items():
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


# 'Итальянский': Dictionary('Итальянский', ...)
dictionaries = dd(str)


state_storage = StateMemoryStorage()
bot = telebot.TeleBot('6147352947:AAGw2dPTsNfXV501DMhsYXzrXlbkBucEU8o',
                    state_storage=state_storage)


@bot.message_handler(commands=['start'])
def start_message(message):
    res = bot.send_message(message.from_user.id,
    f'[prevtext = {message.text}]\nЗдравствуйте!, *{message.from_user.username}*!\n\n' +
    'Я — бот-словарь, созданный для хранения всех ваших слов и их переводов.\n\n' + 
    'Я отлично подхожу как для архивирования необычных слов на родном языке, так и ' + 
    'для изучения нового языка и накопления своего личного лексикона. Приступим?\n\n' + 
    '—'*30 + '\n\n' + '`[>] Для начала создайте словарь с помощью\n' + ' ' * 4 + 'кнопки "Создать словарь"`',
    parse_mode='Markdown'
    )


def got_name_and_emoji(message, name):
    global dictionaries
    
    emoji = message.text
    bot.send_message(message.from_user.id, 
    f'Готово! Новый словарь будет называться `{name} {emoji}`!')

    new_name = (name + ' ' + emoji) if (emoji != ' ') else name
    dictionaries[new_name] = Dictionary(new_name)


def got_name(message):
    name = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_blank = types.KeyboardButton(" ")
    btn_rus = types.KeyboardButton("🇷🇺")
    btn_eng = types.KeyboardButton("🇬🇧")
    btn_ger = types.KeyboardButton("🇩🇪")
    btn_kor = types.KeyboardButton("🇰🇷")
    btn_jap = types.KeyboardButton("🇯🇵")
    btn_chi = types.KeyboardButton("🇨🇳")
    btn_ita = types.KeyboardButton("🇮🇹")
    btn_fra = types.KeyboardButton("🇫🇷")
    btn_spa = types.KeyboardButton("🇪🇸")
    markup.add(btn_blank,
               btn_rus,
               btn_eng,
               btn_ger,
               btn_kor,
               btn_jap,
               btn_chi,
               btn_ita,
               btn_fra,
               btn_spa)

    sent = bot.send_message(message.from_user.id, 
    f'Отлично, давай назовём словарь `{name}`!\n\nТеперь выбери эмодзи, ' +
    'которое будет выступать ярлыком словаря. Ты '+
    'можешь выбрать пустую кнопку, чтобы не добавлять эмодзи', 
    parse_mode='Markdown',
    reply_markup=markup)
    
    bot.register_next_step_handler(sent, got_name_and_emoji, name)


def parse_to_human_readable(dicts):
    if len(dicts.keys()) == 0:
        return 'тут пусто...'
    
    res = ''
    for k, v in dicts.items():
        res += (str(v) + '\n')
    return res
        

@bot.message_handler(commands=['list_of_dictionaries'])
def list_of_dictionaries(message):
    bot.reply_to(message, 
    (f'*Ваши словари*:\n\n' + 
    parse_to_human_readable(dictionaries)),
    parse_mode='Markdown',
    )


@bot.message_handler(commands=['add_dictionary'])
def add_dictionary(message):
    sent = bot.reply_to(message, 'Давайте добавим для вас новый словарь!\n\n' + 
    'Для этого введите его имя')

    bot.register_next_step_handler(sent, got_name)
    


bot.polling(none_stop=True, interval=0)