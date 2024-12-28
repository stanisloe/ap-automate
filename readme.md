# Автоматический вход в криптокошельки
Автоматический вход в кошельки через Adspower по заранее заданной сид фразе и паролю

## Установка
```bash
# Установка репозитория
git clone https://github.com/stanisloe/ap-automate.git

# Переход в папку с репозиторием
cd ap-automate

# Установка виртуального окружения
python -m venv venv
```

### Активация виртуального окружения на Windows
Это нужно делать после каждого запуска консоли
```commandline
.\venv\Scripts\activate.bat
```

### Активация виртуального окружения на Linux и MacOS
Это нужно делать после каждого запуска консоли
```bash
source venv/bin/activate
```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### .env
Далее нужно зайти в Adspower -> API 
- ADSPOWER_URI: значение из строки  "Соединение"
- ADSPOWER_API_KEY: Нужно нажать на "Сбросить" рядом с "API Key" и скопировать новый ключ

Далее нужно поменять значения в командах ниже на свои и выполнить их
```bash
echo ADSPOWER_URI=http://local.adspower.net:50325 >> .env
echo ADSPOWER_API_KEY=FBFE4BA3CA82D13AC5EB743F001CC4C9 >> .env
```


## Запуск
Самая актуальная справка по аргументам запуска

```bash
python run.py --help
```

### Пример запуска
```bash
python run.py --file profiles.csv.bin --extension phantom --extId bfnaelmomeimhlpmgjnjophhpkkoljpa
```
При запуске запросит пароль, если файл зашифрован


## Шифрование
Самая актуальная справка по аргументам запуска

```bash
python cryptor.py --help
```

### Пример запуска
```bash
python cryptor.py --encrypt --file profiles.csv
```
Скрипт зашифрует файл и выдаст на выходе зашифрованный файл с суффиксом .bin(profiles.csv -> profiles.csv.bin)
После запуска скрипт запросит пароль.