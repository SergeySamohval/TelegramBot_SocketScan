#!/usr/bin/env python3
# The socket module in Python is an interface to the Berkeley sockets API.
import socket
# We need to create regular expressions to ensure that the input is correctly formatted.
import re

# Шаблон регулярного выражение для определения правильности ввода IP адреса.
ip_add_example = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
# Шаблон регулярного выражение для определения правильности ввода доменного имени
#ip_add_example = re.compile("^(?!\-)(?:[a-zA-Z\d\-]{0,62}[a-zA-Z\d]\.){1,126}(?!\d+)[a-zA-Z\d]{1,63}$")
# ШАблон регулярного выражения для определения правильности ввода диапазона сканируемых портов.
# нужно ввести "минимальный порт-максимальный порт (пример: 20-80)
port_range_example = re.compile("([0-9]+)-([0-9]+)")
port_min = 0
port_max = 65535

open_ports = []

# спрашиваем пользователя какой IP адрес он хочет просканировать и проводим проверку с нашим рег. выражением
while True:
    ip_add_entered = input("\nКакой IP адрес нужно просканировать: ")
    if ip_add_example.search(ip_add_entered):
        print(f"Введенный IP адрес: {ip_add_entered} ")
        break

while True:
    # выбор диапазона портов для сканирования и проверка этого диапазона с рег. выражением
    print("Введите диапазон портов для сканирования в формате: <мин.порт>-<макс.порт> (пример 25-80)")
    port_range = input("Диапазон портов: ")
    port_range_valid = port_range_example.search(port_range.replace(" ",""))
    if port_range_valid:
        port_min = int(port_range_valid.group(1))
        port_max = int(port_range_valid.group(2))
        break

for port in range(port_min, port_max + 1):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Установка таймаута для подключения
            s.settimeout(0.5)
            # Подключаемся к сокету и если не получается, то в список open_ports не добавляем значение
            s.connect((ip_add_entered, port))
            # Если порт открыт, то доваляем его значение
            open_ports.append(port)

    except:
        # Ничего тут не указывем так как с закрытыми портами мы ничего не делаем
        pass

for port in open_ports:
    print(f"Port {port} is open on {ip_add_entered}.")