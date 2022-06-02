# Парсер документации python и PEP
## Описание
Парсер информации о python с **https://docs.python.org/3/** и  **https://peps.python.org/**
### Перед использованием
Клонируйте репозиторий к себе на компьютер при помощи команд:
```
git clone https://github.com/AleksSpace/bs4_parser_pep.git
```
или
```
git clone git@github.com:AleksSpace/bs4_parser_pep.git
```
или
```
git clone gh repo clone AleksSpace/bs4_parser_pep
```

В корневой папке нужно создать виртуальное окружение и установить зависимости.
```
python3 -m venv venv
```
```
pip install -r requirements.txt
```
### Программа запускается из main.py в папке ./src/
```
python3 main.py [вариант парсера] [аргументы]
```
### Встроенные парсеры
- whats-new   
Парсер выводящий спсок изменений в python.
```
python3 main.py whats-new [аргументы]
```
- latest_versions   
Парсер выводящий список версий python и ссылки на их документацию.
```
python3 main.py latest-versions [аргументы]
```
- download   
Парсер скачивающий zip архив с документацией python в pdf формате.
```
python3 main.py download [аргументы]
```
- pep   
Парсер выводящий список статусов документов pep   
и количество документов в каждом статусе. 
```
python3 main.py pep [аргументы]
```
### Аргументы
Есть возможность указывать аргументы для изменения работы программы:   
- -h, --help
Общая информация о командах.
```
python3 main.py -h
```
- -c, --clear-cache
Очистка кеша перед выполнением парсинга.
```
python3 main.py [вариант парсера] -c
```
- -o {pretty,file}, --output {pretty,file}   
Дополнительные способы вывода данных   
pretty - выводит данные в командной строке в таблице   
file - сохраняет информацию в формате csv в папке ./results/
```
python3 main.py [вариант парсера] -o file
```
### Автор
- [Заикин Алексей](https://github.com/AleksSpace "GitHub аккаунт")