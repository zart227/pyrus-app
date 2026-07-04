# ✅ Проверочный список установки

Используйте этот список для проверки всех шагов установки.

## Подготовка

- [ ] Docker и Docker Compose установлены
  ```bash
  docker --version
  docker compose version
  ```

- [ ] Создан файл `.env` с учетными данными
  ```bash
  ls -la .env
  cat .env  # Проверьте содержимое
  ```

## Установка Nginx на хосте

- [ ] Nginx установлен
  ```bash
  nginx -v
  ```

- [ ] Конфигурация скопирована в `/etc/nginx/sites-available/`
  ```bash
  ls -la /etc/nginx/sites-available/pyrus
  ```

- [ ] Создана символическая ссылка в `/etc/nginx/sites-enabled/`
  ```bash
  ls -la /etc/nginx/sites-enabled/pyrus
  ```

- [ ] Конфигурация Nginx проверена и без ошибок
  ```bash
  sudo nginx -t
  ```

- [ ] Nginx перезапущен
  ```bash
  sudo systemctl status nginx
  ```

## Запуск приложения

- [ ] Скрипт `prod.sh` исполняемый
  ```bash
  ls -la prod.sh
  ```

- [ ] Приложение запущено
  ```bash
  ./prod.sh up
  ```

- [ ] Все контейнеры работают
  ```bash
  ./prod.sh ps
  # Должно показать: db, backend, frontend, nginx (все Up)
  ```

## Проверка работоспособности

- [ ] Backend отвечает
  ```bash
  curl http://localhost:8000/api/health || curl http://localhost:8000
  ```

- [ ] Docker Nginx отвечает
  ```bash
  curl http://localhost:8082
  ```

- [ ] Nginx на хосте проксирует запросы
  ```bash
  curl http://localhost/pyrus/
  ```

- [ ] Приложение доступно через сеть
  ```bash
  # С другого компьютера в сети:
  # http://адрес_сервера/pyrus/
  ```

## Дополнительные проверки

- [ ] Логи не содержат критических ошибок
  ```bash
  ./prod.sh logs
  ```

- [ ] Firewall настроен (если используется)
  ```bash
  sudo ufw status
  ```

- [ ] PostgreSQL работает
  ```bash
  docker compose exec db pg_isready -U pyrus_user
  ```

## Проверка доступности из сети

- [ ] Узнайте IP адрес сервера
  ```bash
  hostname -I
  # Или: ip addr show
  ```

- [ ] Откройте в браузере с другого компьютера
  ```
  http://IP_АДРЕС_СЕРВЕРА/pyrus/
  ```

- [ ] Страница логина загружается
- [ ] Можно войти в систему
- [ ] Приложение работает корректно

## Если что-то не работает

### Backend не запускается
```bash
./prod.sh logs backend
```
Проверьте:
- Правильность данных в `.env`
- Доступность PostgreSQL

### Frontend не загружается
```bash
./prod.sh logs frontend
```
Проверьте:
- Сборку прошла успешно
- Нет ошибок в логах

### Nginx на хосте не работает
```bash
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```
Проверьте:
- Конфигурация корректна (`sudo nginx -t`)
- Порт 80 не занят другим приложением

### Приложение не доступно из сети
Проверьте:
- Firewall разрешает порт 80
  ```bash
  sudo ufw allow 80/tcp
  ```
- Сервер доступен из сети (ping)
  ```bash
  ping адрес_сервера
  ```

## Полезные команды

```bash
# Просмотр всех открытых портов
sudo netstat -tlnp | grep -E '(80|8000|8082|5433)'

# Статус всех сервисов
./prod.sh ps
sudo systemctl status nginx

# Перезапуск всего
./prod.sh restart
sudo systemctl restart nginx

# Просмотр логов
./prod.sh logs           # Все логи
./prod.sh logs backend   # Только backend
./prod.sh logs frontend  # Только frontend
sudo tail -f /var/log/nginx/access.log  # Nginx access log
sudo tail -f /var/log/nginx/error.log   # Nginx error log
```

## Готово! 🎉

Если все пункты отмечены ✅, значит приложение настроено правильно и доступно в корпоративной сети по адресу:

**`http://адрес_вашего_сервера/pyrus/`**

