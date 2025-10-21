# Режим разработки (Development Mode)

## Описание

В режиме разработки доступна автоматическая перезагрузка (hot reload) при изменении файлов:

- **Backend**: Uvicorn с флагом `--reload` автоматически перезапускает сервер при изменении Python файлов
- **Frontend**: Vite dev server с hot module replacement (HMR) для мгновенного обновления Vue компонентов

## Запуск в режиме разработки

### 1. Запустить контейнеры

```bash
docker compose -f docker-compose.dev.yml up --build
```

Или в фоновом режиме:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

### 2. Остановить контейнеры

```bash
docker compose -f docker-compose.dev.yml down
```

### 3. Пересобрать контейнеры (если изменились зависимости)

```bash
docker compose -f docker-compose.dev.yml up --build --force-recreate
```

## Доступ к приложению

- **Приложение (через Nginx)**: http://localhost:8082
- **Frontend (Vite dev server)**: http://localhost:8081
- **Backend API**: http://localhost:8000
- **API документация**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5433

## Особенности режима разработки

### Backend
- Автоматическая перезагрузка при изменении `.py` файлов
- Volume mapping: весь код монтируется в контейнер
- Логи выводятся в реальном времени

### Frontend
- Hot Module Replacement (HMR) - мгновенное обновление без перезагрузки страницы
- Volume mapping: код из `./frontend` монтируется в контейнер
- Исключен `node_modules` для избежания конфликтов
- WebSocket соединение для HMR через Nginx

### Nginx
- Проксирует запросы к Vite dev server (порт 5173)
- Поддержка WebSocket для HMR
- Проксирование API запросов к backend

## Просмотр логов

### Все сервисы
```bash
docker compose -f docker-compose.dev.yml logs -f
```

### Конкретный сервис
```bash
docker compose -f docker-compose.dev.yml logs -f backend
docker compose -f docker-compose.dev.yml logs -f frontend
docker compose -f docker-compose.dev.yml logs -f nginx
```

## Production режим

Для продакшн развертывания используйте обычный docker-compose:

```bash
docker compose up -d --build
```

В продакшн режиме:
- Frontend собирается статически (Vue build)
- Backend работает без auto-reload
- Nginx раздает статические файлы из собранного frontend

## Переключение между режимами

### Development → Production
```bash
docker compose -f docker-compose.dev.yml down
docker compose up -d --build
```

### Production → Development
```bash
docker compose down
docker compose -f docker-compose.dev.yml up -d --build
```

## Troubleshooting

### Frontend не обновляется автоматически
- Убедитесь что используете `docker-compose.dev.yml`
- Проверьте что volume mapping настроен правильно
- Попробуйте пересобрать: `docker compose -f docker-compose.dev.yml up --build --force-recreate frontend`

### Backend не перезагружается
- Проверьте логи: `docker compose -f docker-compose.dev.yml logs -f backend`
- Убедитесь что файлы сохраняются в монтированном volume
- Проверьте синтаксис Python файлов

### Ошибка WebSocket
- Проверьте nginx логи: `docker compose -f docker-compose.dev.yml logs -f nginx`
- Убедитесь что frontend контейнер запущен
- Проверьте порты не заняты другими процессами

