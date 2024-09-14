## Создание и активация виртуального окружения

```bash
python -m venv venv
venv\Scripts\activate
```

## Установка зависимостей


```bash
pip install -r requirements.txt
```

## Сохранение новых зависимостей

```bash
pip freeze > requirements.txt
```

## Установка переменных (дописать)


## Установка credential для гугл таблиц

Необходимо если нужно сохранять данные в гугл таблицу

1. Создать проект в Google Cloud Console
2. Включить Google Sheets API для вашего проекта.
3. Создайте учетные данные OAuth 2.0 и получите файл credentials.json
4. Выдать доступ к таблице боту, почта в файле credentials.json

## Запуск скрипта (дописать)