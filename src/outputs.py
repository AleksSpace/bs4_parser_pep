import csv
import datetime as dt
import logging
from prettytable import PrettyTable
from constants import BASE_DIR, DATETIME_FORMAT


# Контроль вывода результатов парсинга.
def control_output(results, cli_args):
    """
    Анализирует атрибуты, указанные при запуске программы.
    По ним определяет, в каком виде нужно предоставить данные.
    """
    # Чтобы не обращаться дважды к атрибуту объекта в условиях if, elif,
    # сохраним значение в переменную.
    output = cli_args.output
    if output == 'pretty':
        # Вывод данных в PrettyTable.
        pretty_output(results)
    elif output == 'file':
        # Вывод данных в файл csv. Саму функцию напишем позже.
        file_output(results, cli_args)
    else:
        # Вывод данных по умолчанию — в терминал построчно.
        default_output(results)

# Вывод данных в терминал построчно.
def default_output(results):
    """
    Функция для вывода результата работы программы в консоль.
    """
    # Печатаем список results построчно.
    for row in results:
        print(*row)    

# Вывод данных в формате PrettyTable.
def pretty_output(results):
    """
    Функция для вывода результата работы
    программы в коносль в виде таблицы.
    """
    # Инициализируем объект PrettyTable.
    table = PrettyTable()
    # В качестве заголовков устанавливаем первый элемент списка.
    table.field_names = results[0]
    # Выравниваем всю таблицу по левому краю.
    table.align = 'l'
    # Добавляем все строки, начиная со второй (с индексом 1).
    table.add_rows(results[1:])
    # Печатаем таблицу.
    print(table)

# Создание директории с результатами парсинга.
def file_output(results, cli_args):
    """
    Функция для вывода результата работы программы в файл csv.
    """
    # Сформируйте путь до директории results.
    results_dir = BASE_DIR / 'results'
    # Создайте директорию.
    results_dir.mkdir(exist_ok=True)
    # Отсюда начинается новый код. 
    # Получаем режим работы парсера из аргументов командной строки.
    parser_mode = cli_args.mode
    # Получаем текущие дату и время.
    now = dt.datetime.now()
    # Сохраняем текущие дату-время в указанном формате. 
    # Результат будет выглядеть вот так: 2022-05-31_13-30-41.
    now_formatted = now.strftime(DATETIME_FORMAT)
    # Собираем имя файла из полученных переменных: 
    # «режим работы программы» + «дата и время записи» + формат (.csv).
    file_name = f'{parser_mode}_{now_formatted}.csv'
    # Получаем абсолютный путь к файлу с результатами.
    file_path = results_dir / file_name
    # Отсюда начинается новый код.
    # Через контекстный менеджер открываем файл по сформированному ранее пути 
    # в режиме записи 'w', в нужной кодировке utf-8.
    with open(file_path, 'w', encoding='utf-8') as f:
        # Создаём «объект записи» writer.
        writer = csv.writer(f, dialect='unix')
        # Передаём в метод writerows список с результатами парсинга.
        writer.writerows(results)
    # Допишите этот код в самом конце функции.
    logging.info(f'Файл с результатами был сохранён: {file_path}')