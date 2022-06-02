import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging

from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    """
    Парсер выводящий спсок изменений в python.
    """
    # Вместо константы WHATS_NEW_URL, используйте переменную whats_new_url.
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        # Если основная страница не загрузится, программа закончит работу.
        return
    soup = BeautifulSoup(response.text, features='lxml')

    # Шаг 1-й: поиск в "супе" тега section с нужным id. Парсеру нужен только 
    # первый элемент, поэтому используется метод find().
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})

    # Шаг 2-й: поиск внутри main_div следующего тега div с классом toctree-wrapper.
    # Здесь тоже нужен только первый элемент, используется метод find().
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    # Шаг 3-й: поиск внутри div_with_ul всех элементов списка li с классом toctree-l1.
    # Нужны все теги, поэтому используется метод find_all().
    sections_by_python = div_with_ul.find_all('li', attrs={'class': 'toctree-l1'})
    # Инициализируйте пустой список results.
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    # Печать первого найденного элемента.
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            # Если страница не загрузится, программа перейдёт к следующей ссылке.
            continue
        soup = BeautifulSoup(response.text, features='lxml')  # Сварите "супчик".
        h1 = find_tag(soup, 'h1')  # Найдите в "супе" тег h1.
        dl = find_tag(soup, 'dl')  # Найдите в "супе" тег dl.
        dl_text = dl.text.replace('\n', ' ')
        # На печать теперь выводится переменная dl_text — без пустых строчек.
        # Добавьте в список ссылки и текст из тегов h1 и dl в виде кортежа.
        results.append(
            (version_link, h1.text, dl_text)
        )

    return results

def latest_versions(session):
    """
    Парсер выводящий список версий python и ссылки на их документацию.
    """
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    # Перебор в цикле всех найденных списков.
    for ul in ul_tags:
        # Проверка, есть ли искомый текст в содержимом тега.
        if 'All versions' in ul.text:
            # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all('a')
            # Остановка перебора списков.
            break
    # Если нужный список не нашёлся,
    # вызывается исключение и выполнение программы прерывается.
    else:
        raise Exception('Ничего не нашлось')

    # Список для хранения результатов.
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    # Шаблон для поиска версии и статуса:
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    # Цикл для перебора тегов <a>, полученных ранее.
    for a_tag in a_tags:
        # Извлечение ссылки.
        link = a_tag['href']
        # Поиск паттерна в ссылке.
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:  
            # Если строка соответствует паттерну,
            # переменным присываивается содержимое групп, начиная с первой.
            version, status = text_match.groups()
        else:  
            # Если строка не соответствует паттерну,
            # первой переменной присваивается весь текст, второй — пустая строка.
            version, status = a_tag.text, ''  
        # Добавление полученных переменных в список в виде кортежа.
        results.append(
            (link, version, status)
        )
    return results

def download(session):
    """
    Парсер скачивающий zip архив с документацией python в pdf формате.
    """
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a', attrs={'href': re.compile(r'.+pdf-a4\.zip$')})
    # Сохраните в переменную содержимое атрибута href.
    pdf_a4_link = pdf_a4_tag['href']
    # Получите полную ссылку с помощью функции urljoin.
    archive_url = urljoin(downloads_url, pdf_a4_link)
    # Имя файла
    filename = archive_url.split('/')[-1]

    # Сформируйте путь до директории downloads.
    downloads_dir = BASE_DIR / 'downloads'
    # Создайте директорию.
    downloads_dir.mkdir(exist_ok=True)
    # Получите путь до архива, объединив имя файла с директорией.
    archive_path = downloads_dir / filename

    # Загрузка архива по ссылке.
    response = session.get(archive_url)

    # В бинарном режиме открывается файл на запись по указанному пути.
    with open(archive_path, 'wb') as file:
        # Полученный ответ записывается в файл.
        file.write(response.content)
    # Допишите этот код в самом конце функции.
    logging.info(f'Архив был загружен и сохранён: {archive_path}')

def pep(session):
    """
    Парсер выводящий список статусов документов pep
    и количество документов в каждом статусе.
    Также проверяет соответствие статусов на главной
    и на отдельной странице документа.
    """
    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')
    results = [('Cтатус', 'Количество')]
    pep_sum = {}
    total_sum = 0
    diff = []
    for tr_tag in tqdm(tr_tags):
        total_sum += 1
        a_tag = find_tag(tr_tag, 'a', attrs={'class': 'reference external'})
        pep_url = urljoin(PEP_URL, a_tag['href'])
        response = get_response(session, pep_url)
        soup = BeautifulSoup(response.text, features='lxml')
        dl_tag = find_tag(soup, 'dl', attrs={'class': 'rfc2822 field-list simple'})
        dd_tag = find_tag(
            dl_tag, 'dt', attrs={'class': 'field-even'}
        ).find_next_sibling('dd')
        status = dd_tag.string
        status_in_main_page = find_tag(tr_tag, 'td').string[1:]
        if status not in EXPECTED_STATUS[status_in_main_page]:
            diff.append([pep_url, status, status_in_main_page])
        if status in pep_sum:
            pep_sum[status] += 1
        else:
            pep_sum[status] = 1
    if diff:
        for pep_url, status, status_in_main_page in diff:
            logging.info(
                f'Несовпадающие статусы:'
                f'{pep_url}'
                f'Cтатус в карточке: {status}'
                f'Ожидаемые статусы: {EXPECTED_STATUS[status_in_main_page]}'
            )
    for key, value in pep_sum.items():
        results.append((key, value))
    results.append(('Total: ', total_sum))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}

def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')
    
    # Создание кеширующей сессии.
    session = requests_cache.CachedSession()
    # Если был передан ключ '--clear-cache', то args.clear_cache == True.
    if args.clear_cache:
        # Очистка кеша.
        session.cache.clear()
    
    # Получение из аргументов командной строки нужного режима работы.
    parser_mode = args.mode
    
    # С вызовом функции передаётся и сессия.
    results = MODE_TO_FUNCTION[parser_mode](session)

    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)
    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')

if __name__ == '__main__':
    main()
