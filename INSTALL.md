# Инструкция по настройке доступа через /pyrus

## Предварительные требования

- Docker и Docker Compose установлены
- Права sudo на сервере
- Порты 80, 8000, 8082, 5433 доступны

## Шаги установки

### 1. Установка Nginx на хост-сервере

```bash
sudo apt update
sudo apt install -y nginx
```

Проверьте, что Nginx установлен:
```bash
sudo systemctl status nginx
```

### 2. Настройка Nginx для reverse proxy

Скопируйте конфигурацию:
```bash
sudo cp nginx-host.conf /etc/nginx/sites-available/pyrus
```

Создайте символическую ссылку для активации:
```bash
sudo ln -s /etc/nginx/sites-available/pyrus /etc/nginx/sites-enabled/
```

Проверьте конфигурацию на ошибки:
```bash
sudo nginx -t
```

Если проверка прошла успешно, перезапустите Nginx:
```bash
sudo systemctl restart nginx
```

### 3. Запуск приложения

Сделайте скрипт исполняемым:
```bash
chmod +x prod.sh
```

Запустите приложение в production режиме:
```bash
./prod.sh up
```

### 4. Проверка работы

Откройте браузер и перейдите по адресу:
```
http://адрес_вашего_сервера/pyrus/
```

Приложение должно быть доступно для всей корпоративной сети.

## Управление приложением

### Просмотр логов
```bash
./prod.sh logs           # Все сервисы
./prod.sh logs backend   # Только backend
./prod.sh logs frontend  # Только frontend
./prod.sh logs nginx     # Только nginx
```

### Перезапуск
```bash
./prod.sh restart        # Все сервисы
./prod.sh restart nginx  # Только nginx
```

### Остановка
```bash
./prod.sh down
```

### Пересборка
```bash
./prod.sh rebuild
```

### Переключение в dev режим
```bash
./prod.sh dev
```

## Проверка статуса

### Статус Docker контейнеров
```bash
./prod.sh ps
```

### Статус Nginx на хосте
```bash
sudo systemctl status nginx
```

### Проверка портов
```bash
sudo netstat -tlnp | grep -E '(80|8000|8082|5433)'
```

## Устранение неполадок

### Приложение не открывается

1. Проверьте, что все контейнеры запущены:
   ```bash
   ./prod.sh ps
   ```

2. Проверьте логи:
   ```bash
   ./prod.sh logs
   ```

3. Проверьте конфигурацию Nginx:
   ```bash
   sudo nginx -t
   ```

4. Проверьте, что порт 8082 доступен:
   ```bash
   curl http://localhost:8082
   ```

### Проблемы с базой данных

Проверьте логи базы данных:
```bash
./prod.sh logs db
```

### Проблемы с правами доступа

Если возникают проблемы с правами доступа к файлам:
```bash
sudo chown -R $USER:$USER /home/rustem/pyrus-app
```

## Безопасность

### Firewall

Откройте порт 80 для корпоративной сети:
```bash
sudo ufw allow 80/tcp
```

Если используется специфический диапазон IP корпоративной сети:
```bash
sudo ufw allow from 192.168.0.0/16 to any port 80 proto tcp
```

### SSL/HTTPS (опционально)

Для настройки HTTPS с Let's Encrypt:

1. Установите Certbot:
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   ```

2. Получите сертификат (замените your-domain.com):
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. Certbot автоматически обновит конфигурацию Nginx

## Резервное копирование

### База данных

Создание резервной копии:
```bash
docker compose exec db pg_dump -U pyrus_user pyrus_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

Восстановление из резервной копии:
```bash
docker compose exec -T db psql -U pyrus_user pyrus_db < backup_20241021_120000.sql
```

## Обновление приложения

1. Остановите приложение:
   ```bash
   ./prod.sh down
   ```

2. Обновите код (git pull или замените файлы)

3. Пересоберите и запустите:
   ```bash
   ./prod.sh rebuild
   ```

## Мониторинг

### Просмотр использования ресурсов
```bash
docker stats
```

### Проверка дискового пространства
```bash
df -h
docker system df
```

### Очистка неиспользуемых Docker ресурсов
```bash
docker system prune -a
```

