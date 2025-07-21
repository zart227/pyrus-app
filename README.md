# Pyrus Tasks API

FastAPI приложение для работы с задачами Pyrus.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и добавьте в него ваши учетные данные Pyrus:
```
PYRUS_LOGIN=your_login@pyrus.com
PYRUS_SECURITY_KEY=your_security_key
```

## Запуск

```bash
uvicorn main:app --reload
```

Приложение будет доступно по адресу: http://localhost:8000

## API Endpoints

- `GET /tasks` - Получить список всех задач
- `GET /tasks/{task_id}` - Получить конкретную задачу по ID
- `GET /inbox` - Получить задачи из входящих

## Документация API

После запуска приложения, документация Swagger UI будет доступна по адресу:
http://localhost:8000/docs 