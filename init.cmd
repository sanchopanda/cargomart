REM Установка политики выполнения скриптов PowerShell
powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser"

REM Создание виртуального окружения
C:\Users\Dir\AppData\Local\Programs\Python\Python313\python.exe -m venv venv

REM Активация виртуального окружения
call venv\Scripts\activate

REM Установка зависимостей из requirements.txt
C:\Users\Dir\AppData\Local\Programs\Python\Python313\python.exe -m pip install -r requirements.txt

echo Установка завершена.
