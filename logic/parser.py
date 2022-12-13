import re
import json
import argparse
from collections import Counter, deque

parser = argparse.ArgumentParser(description='Process access.log')
parser.add_argument('-f', dest='file', action='store', help='Path to logfile', default='access.log')
args = parser.parse_args()

"""
1. Сперва рекомендую отыскать файл с логами в ручном режиме, чтоб в п.2 вставить путь до файла
команда: locate access.log
2. Запускать парсер командой: python parser.py -f ПУТЬ_ИЗ_ШАГА_1
"""

def reader(filename):
    # Регулярные выражения
    reg_ip = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    reg_method = r'\] \"(POST|GET|PUT|DELETE|HEAD)'
    reg_time = r'\d\d\d*$'

    with open(filename) as file:
        requests = 0  # Счетчик запросов
        ip_list = []  # Список всех IP адресов
        method_list = []  # Список всех методов
        biggest_time = deque(['1'], maxlen=3)  # Список с наибольшим временем запроса
        biggest_request = deque(maxlen=3)  # Список запросов с наибольшим временем
        for line in file:
            requests += 1  # Подсчет количества строк
            try:
                ip = re.findall(reg_ip, line)
                ip_list.append(ip[0])  # Добавление адреса ip в список
            except IndexError:
                pass
            try:
                method = re.findall(reg_method, line)
                method_list.append(method[0])  # Добавление метода в список
            except IndexError:
                pass
            # Пополнение списка топ 10 самых долгих запросов
            time = re.findall(reg_time, line)
            int_time = int(time[0])
            for i in biggest_time:
                int_i = int(i[0])
                if int_time > int_i:
                    biggest_request.appendleft(line)
                    biggest_time.appendleft(time)
                    break

    top3ip = Counter(ip_list).most_common(3)  # Топ 3 ip адресов
    method_count = Counter(method_list)  # Словарь с количеством использования всех методов

    biggest_request_list = []
    for i in biggest_request:
        biggest_request_list.append(i)

    json_file = {
        "Top 3 IP": top3ip,
        "Methods": [
            {
                "GET": method_count["GET"],
                "POST": method_count["POST"],
                "PUT": method_count["PUT"],
                "DELETE": method_count["DELETE"],
                "HEAD": method_count["HEAD"]
            }
        ],
        "Total requests": requests,
        "Top 3 longest requests": biggest_request_list
    }

    with open("result.json", "w", encoding="utf-8") as file:
        try:
            json_schema = json.dumps(json_file, indent=4)
            file.write(json_schema)
        except OSError:
            print("Load json file failed")


if __name__ == '__main__':
    reader(args.file)
