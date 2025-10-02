# 🔧 Решение проблемы с портом в app.py

## 🚨 Проблема

При запуске `python3 app.py` возникала ошибка:

```
Address already in use
Port 5000 is in use by another program. Either identify and stop that program, or start the server with a different port.
On macOS, try disabling the 'AirPlay Receiver' service from System Preferences -> General -> AirDrop & Handoff.
```

## 🔍 Причина

Порт 5000 занят процессом **AirPlay Receiver** на macOS:

```bash
$ lsof -i :5000
COMMAND    PID         USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
ControlCe 1335 evgenijbutov   10u  IPv4 0x3d81c7b07d9b2d79      0t0  TCP *:commplex-main (LISTEN)
```

`ControlCe` - это системный процесс macOS, который управляет AirPlay Receiver.

## ✅ Решения

### Решение 1: Запуск на другом порту (Рекомендуется)

```bash
# Запуск на порту 5002
python3 app.py --port 5002

# Или через Flask CLI
flask run --port 5002
```

### Решение 2: Отключение AirPlay Receiver

1. Открыть **System Preferences** → **General**
2. Найти **AirDrop & Handoff**
3. Отключить **AirPlay Receiver**
4. Перезапустить сервер на порту 5000

### Решение 3: Изменение конфигурации Flask

В `app.py` или `config.py`:

```python
# Изменить порт по умолчанию
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
```

## 🌐 Обновленные URL

После запуска на порту 5002, все URL изменились:

### Основные страницы:
- **Главная**: `http://localhost:5002/`
- **Логин**: `http://localhost:5002/auth/nl/login`
- **Админ**: `http://localhost:5002/admin/`

### Membership функции:
- **Upgrade**: `http://localhost:5002/membership/upgrade`
- **Card**: `http://localhost:5002/membership/card`
- **Checkout**: `http://localhost:5002/membership/checkout`
- **Verify**: `http://localhost:5002/membership/verify/MNT-XXXXX`

### Админ-панель:
- **Dashboard**: `http://localhost:5002/admin/dashboard`
- **Membership Test**: `http://localhost:5002/admin/membership-test`

## 🔧 Проверка статуса

### Проверить, что сервер работает:
```bash
curl -I http://localhost:5002/
```

**Ожидаемый ответ:**
```
HTTP/1.1 200 OK
Server: Werkzeug/3.1.3 Python/3.12.3
```

### Проверить доступность админ-панели:
```bash
curl -I http://localhost:5002/admin/membership-test
```

**Ожидаемый ответ:**
```
HTTP/1.1 302 FOUND
Location: /auth/nl/login
```

## 📋 Рекомендации

### Для разработки:
- Используйте порт 5002 или другой свободный порт
- Не отключайте AirPlay Receiver (может понадобиться для других приложений)

### Для продакшена:
- Настройте прокси-сервер (nginx/Apache)
- Используйте стандартные порты (80/443)
- Настройте переменные окружения для портов

## 🚀 Быстрый старт

```bash
# 1. Остановить все процессы Flask
pkill -f "python3 app.py"

# 2. Запустить на порту 5002
python3 app.py --port 5002

# 3. Проверить работу
curl -I http://localhost:5002/
```

## 📝 Примечания

- **AirPlay Receiver** - это системная функция macOS
- Отключение может повлиять на другие приложения
- Порт 5002 - безопасная альтернатива
- Все функции работают одинаково на любом порту

**Статус**: ✅ Решено  
**Порт**: 5002  
**Дата**: 2025-10-02



