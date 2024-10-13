## Создание и активация виртуального окружения

```bash
python -m venv venv
venv\Scripts\activate
```

Если активация виртуального окружения вызывает ошибку, нужно открыть PowerShell от имени администратора и выполнить команду

```bash
Set-ExecutionPolicy RemoteSigned
```

## Установка зависимостей


```bash
pip install -r requirements.txt
```

## Сохранение новых зависимостей

```bash
pip freeze > requirements.txt
```

## Установка переменных 

выполнить

```bash
copy .env.example .env
```

или скопировать/создать вручную, прописать в .env свои значения

## Запуск скрипта 

```bash
python main.py
```