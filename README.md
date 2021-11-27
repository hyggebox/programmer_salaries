# Сравнение вакансий программистов

Утилита собирает данные по вакансиям программистов на наиболее популярных языках программирования с сайтов 
[hh.ru](https://hh.ru/) и [SuperJob](https://www.superjob.ru/). 
Вычисляет среднюю зарплату, указанную в вакансиях для Москвы, и выводит данные выводятся в консоль в табличном виде.

### Как установить


- Для работы скрипта необходим api-ключ SuperJob, получить который можно зарегистрировавшись
на сайте [api.superjob.ru](https://api.superjob.ru/)


- Скачайте код из репозитория. Api-ключ должен быть сохранен в файле .env:

```
SUPERJOB_KEY=<ваш_api-ключ>
```

- Python3 должен быть уже установлен. Используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:

```
pip install -r requirements.txt
```

- Запустите сайт командой `python` (или `python3`, если есть конфликт с Python2):

```
python main.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).