import telebot
from telebot import types
import socket
import re

# Открываем файл txt берем от туда токен.
with open("token.txt") as f:
    Token = f.read().strip()

bot = telebot.TeleBot(Token)

# Создаем список и помещаем туда ID пользователя телеги.
users = [1254402357]

# Шаблон регулярного выражение для определения правильности ввода IP адреса.
ip_add_example = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
# Шаблон регулярного выражение для определения правильности ввода доменного имени
DomainName_add_example = re.compile("^(?!\-)(?:[a-zA-Z\d\-]{0,62}[a-zA-Z\d]\.){1,126}(?!\d+)[a-zA-Z\d]{1,63}$")
# ШАблон регулярного выражения для определения правильности ввода диапазона сканируемых портов.
# Нужно ввести "минимальный порт-максимальный порт (пример: 20-80)
port_range_example = re.compile("([0-9]+)-([0-9]+)")
port_min = 0
port_max = 65535

open_ports = []

# Cоздаем хедер и назначаем инлайновые кнопки, а также проводим проверку пользователя по его id
# в телеграмме. Если id не добавлен в список, то инлайновые кнопки после команды /start не выводим.
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id in users:
        markup_inline = types.InlineKeyboardMarkup()
        itemIP = types.InlineKeyboardButton(text="IP адрес", callback_data="IP")
        itemDomainName = types.InlineKeyboardButton(text="Доменное имя", callback_data="DomainName")

        markup_inline.add(itemIP, itemDomainName)
        bot.send_message(message.chat.id, message.from_user.first_name +
                    ",что хотите сканировать?", reply_markup=markup_inline)


    elif message.chat.id not in users:
        bot.send_message(message.chat.id, message.from_user.first_name +
                    ", извини, но у тебя нет доступа!")

# Cоздаем обработчик обратного запроса от пользователя.
@bot.callback_query_handler(func = lambda call: True)
def answer(call):
    # В случае выбора кнопки "IP адрес" выполняем функцию "user_answer_IP".
    if call.data == "IP":
        sent1 = bot.send_message(call.message.chat.id, "Введите IP адрес: ")
        bot.register_next_step_handler(sent1, user_answer_IP)
    # В случае выбора кнопки "Доменное имя" выполняем функцию "user_answer_DimainName".
    elif call.data == "DomainName":
        sent1 = bot.send_message(call.message.chat.id, "Введите доменное имя: ")
        bot.register_next_step_handler(sent1, user_answer_DomainName)

# Введенный пользователем IP адрес сравниваем с шаблоном регулярного выражения, назначаем его в качестве
# глобальной переменной "ip_add_entered", просим пользователя ввести диапазон портов для сканирования и
# выполняем функцию "user_answer_port_range".
def user_answer_IP(message):
    global ip_add_entered
    ip_add_entered = message.text
    if ip_add_example.search(ip_add_entered):
        sent2 = bot.send_message(message.chat.id, "Введенный IP адрес: " + ip_add_entered +
                         ".\n" + "Введите диапазон портов для сканирования в формате: "
                                 "<мин.порт>-<макс.порт> (пример 25-80)")
        bot.register_next_step_handler(sent2, user_answer_port_range)
    # В случае,если введенный IP адрес не соответсвует шаблону, то сообщаем об этом пользователю
    # и выдаем ему повторно инлайновые кнопки.
    else:
        markup_inline = types.InlineKeyboardMarkup()
        itemIP = types.InlineKeyboardButton(text="IP адрес", callback_data="IP")
        itemDomainName = types.InlineKeyboardButton(text="Доменное имя", callback_data="DomainName")

        markup_inline.add(itemIP, itemDomainName)

        bot.send_message(message.chat.id, "Введите верный IP адреc. \n" + ip_add_entered
                         + " - это несуществующий IP адрес.\n" +
                         message.from_user.first_name + "!" +
                         " Что хотите сканировать?", reply_markup=markup_inline)

# Введенное пользователем доменное имя сравниваем с шаблоном регулярного выражения, назначаем его в
# качестве глобальной переменной "id_add_entered", просим пользователя ввести диапазон портов для
# сканирования и выполняем фунцию "user_answer_port_range".
def user_answer_DomainName(message):
    global ip_add_entered
    ip_add_entered = message.text
    if DomainName_add_example.search(ip_add_entered):
        sent2 = bot.send_message(message.chat.id, "Введенное доменное имя: " + ip_add_entered +
                         ".\n" + "Введите диапазон портов для сканирования в формате: "
                                 "<мин.порт>-<макс.порт> (пример 25-80)")
        bot.register_next_step_handler(sent2, user_answer_port_range)
    # В случае,если введенное доменное имя не соответсвует шаблону, то сообщаем об этом пользователю
    # и выдаем ему повторно инлайновые кнопки.
    else:
        markup_inline = types.InlineKeyboardMarkup()
        itemIP = types.InlineKeyboardButton(text="IP адрес", callback_data="IP")
        itemDomainName = types.InlineKeyboardButton(text="Доменное имя", callback_data="DomainName")

        markup_inline.add(itemIP, itemDomainName)

        bot.send_message(message.chat.id, "Введите верное доменное имя. \n" + ip_add_entered
                         + " - это неверное доменное имя.\n" +
                         message.from_user.first_name + "!" +
                         " Что хотите сканировать?", reply_markup=markup_inline)
# Сравниваем введенный диапазон портов для сканирования с шаблоном ругулярного выражения и
# и проводим сканирование.
def user_answer_port_range(message):
    port_range = message.text
    port_range_valid = port_range_example.search(port_range.replace(" ", ""))
    if port_range_valid:
        port_min = int(port_range_valid.group(1))
        port_max = int(port_range_valid.group(2))

        for port in range(port_min, port_max + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Установка таймаута для подключения.
                    s.settimeout(0.5)
                # Подключаемся к сокету и если не получается, то в список open_ports не добавляем значение.
                    s.connect((ip_add_entered, port))
                # Если порт открыт, то доваляем его значение.
                    open_ports.append(port)
            except:
                pass
        # Ничего тут не указывем так как с закрытыми портами мы ничего не делаем.
        for port in open_ports:
            bot.send_message(message.chat.id, f"Порт {port} открыт на {ip_add_entered}.")
            break

    else:
        bot.send_message(message.chat.id, message.from_user.first_name +
                         ", был введен неправильный диапазон портов.")
        return start(message)




bot.infinity_polling()
