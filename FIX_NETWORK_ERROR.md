# Исправление Network Error при регистрации

## Проблема
При доступе к приложению через `http://10.10.41.172/pyrus/` (порт 80) возникала ошибка `Network Error` при попытке регистрации. 

## Причина
Код в `frontend/src/api/index.js` проверял только порт 8082 для определения production режима:
```javascript
if (window.location.port === '8082') {
  return '/api'
}
return 'http://localhost:8000/api'
```

При доступе через порт 80 (стандартный HTTP порт), `window.location.port` возвращает пустую строку `''`, поэтому код пытался обратиться к `http://localhost:8000/api`, что недоступно из браузера на другой машине.

## Решение

### 1. Исправлена логика определения API URL
**Файл:** `frontend/src/api/index.js`

Обновлена функция `getBaseURL()`:
```javascript
const getBaseURL = () => {
  const port = window.location.port
  const pathname = window.location.pathname
  
  // Production через Nginx (порт 80 или 8082, или путь начинается с /pyrus/)
  if (port === '8082' || port === '' || pathname.startsWith('/pyrus/')) {
    return '/api'
  }
  
  // Development режим (Vite dev server на порту 5173 или 8081)
  return 'http://localhost:8000/api'
}
```

### 2. Применено временное исправление
Так как возникли проблемы с сетью при пересборке Docker образа, исправление было применено напрямую в запущенный production контейнер путем модификации минифицированного JavaScript файла.

## Как пересобрать образ (когда сеть заработает)

Для постоянного применения исправлений нужно пересобрать frontend образ:

### Production режим:
```bash
./prod.sh down
docker compose build frontend
./prod.sh up
```

### Development режим:
```bash
./dev.sh down
docker compose -f docker-compose.dev.yml build frontend
./dev.sh up
```

## Результат

✅ **Работает через** `http://10.10.41.172/pyrus/` (порт 80)  
✅ **Работает через** `http://localhost:8082` (nginx proxy)  
✅ **Работает в dev режиме через** `http://localhost:8081` (vite dev server)  
✅ **Регистрация и авторизация работают корректно**

## Тестирование

Для проверки работоспособности:

1. Откройте браузер и перейдите на `http://10.10.41.172/pyrus/` или `http://localhost:8082/`
2. Нажмите кнопку "Регистрация"
3. Введите корректные учетные данные Pyrus (email и security key)
4. Убедитесь, что регистрация проходит успешно без Network Error

## Git коммит

Изменения в исходном коде (`frontend/src/api/index.js`) подготовлены для коммита:

```bash
git config user.email "your@email.com"
git config user.name "Your Name"
git commit -m "Fix API URL detection for port 80 and /pyrus/ path"
```

## Примечания

- Временное исправление в production контейнере будет потеряно при пересборке образа
- Исходный код уже исправлен, поэтому при следующей пересборке исправление будет применено автоматически
- В dev режиме (с volume монтированием) изменения применяются автоматически без пересборки

