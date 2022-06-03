import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT

CHOICES = {
    'pretty': 'pretty',
    'file': 'file',
}


def control_output(results, cli_args):
    """
    Анализирует атрибуты, указанные при запуске программы.
    По ним определяет, в каком виде нужно предоставить данные.
    """
    output = cli_args.output
    if output == CHOICES['pretty']:
        pretty_output(results)
    elif output == CHOICES['file']:
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results):
    """
    Функция для вывода результата работы программы в консоль.
    """
    for row in results:
        print(*row)


def pretty_output(results):
    """
    Функция для вывода результата работы
    программы в коносль в виде таблицы.
    """
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """
    Функция для вывода результата работы программы в файл csv.
    """
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
