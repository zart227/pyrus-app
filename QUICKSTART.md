# Быстрый старт: Настройка доступа через /pyrus

## Подготовка: Создайте .env

```bash
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
```

**Примечание:** `PYRUS_LOGIN` и `PYRUS_SECURITY_KEY` больше не требуются! Используйте регистрацию через веб-интерфейс.

## 3 шага для запуска

### Шаг 1: Установите Nginx
```bash
sudo apt update && sudo apt install -y nginx
```

### Шаг 2: Настройте reverse proxy
```bash
# Скопируйте конфигурацию
sudo cp nginx-host.conf /etc/nginx/sites-available/pyrus

# Активируйте конфигурацию
sudo ln -s /etc/nginx/sites-available/pyrus /etc/nginx/sites-enabled/

# Проверьте и перезапустите
sudo nginx -t && sudo systemctl restart nginx
```

### Шаг 3: Запустите приложение
```bash
./prod.sh up
```

## Готово! 🎉

Приложение доступно по адресу:
```
http://адрес_вашего_сервера/pyrus/
```

## Полезные команды

```bash
./prod.sh logs      # Просмотр логов
./prod.sh ps        # Статус контейнеров
./prod.sh restart   # Перезапуск
./prod.sh down      # Остановка
```

📚 Подробная инструкция: см. `INSTALL.md`

