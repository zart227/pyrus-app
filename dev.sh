#!/bin/bash

# Скрипт для управления режимом разработки

case "$1" in
  up)
    echo "🚀 Запуск в режиме разработки (с hot reload)..."
    docker compose -f docker-compose.dev.yml up -d --build
    echo ""
    echo "✅ Контейнеры запущены!"
    echo ""
    echo "📍 Доступ к приложению:"
    echo "   - Приложение (Nginx):      http://localhost:8082"
    echo "   - Frontend (Vite dev):     http://localhost:8081"
    echo "   - Backend API:             http://localhost:8000"
    echo "   - API документация:        http://localhost:8000/docs"
    echo ""
    echo "📝 Команды:"
    echo "   Логи:           ./dev.sh logs"
    echo "   Остановить:     ./dev.sh down"
    echo "   Статус:         ./dev.sh ps"
    ;;
    
  down)
    echo "🛑 Остановка dev контейнеров..."
    docker compose -f docker-compose.dev.yml down
    echo "✅ Контейнеры остановлены"
    ;;
    
  logs)
    if [ -z "$2" ]; then
      echo "📋 Логи всех сервисов (Ctrl+C для выхода)..."
      docker compose -f docker-compose.dev.yml logs -f
    else
      echo "📋 Логи сервиса: $2 (Ctrl+C для выхода)..."
      docker compose -f docker-compose.dev.yml logs -f "$2"
    fi
    ;;
    
  ps)
    echo "📊 Статус контейнеров:"
    docker compose -f docker-compose.dev.yml ps
    ;;
    
  restart)
    if [ -z "$2" ]; then
      echo "🔄 Перезапуск всех контейнеров..."
      docker compose -f docker-compose.dev.yml restart
    else
      echo "🔄 Перезапуск сервиса: $2..."
      docker compose -f docker-compose.dev.yml restart "$2"
    fi
    echo "✅ Перезапуск завершен"
    ;;
    
  rebuild)
    echo "🔨 Пересборка контейнеров..."
    docker compose -f docker-compose.dev.yml up -d --build --force-recreate
    echo "✅ Пересборка завершена"
    ;;
    
  prod)
    echo "🏭 Переключение на production режим..."
    docker compose -f docker-compose.dev.yml down
    docker compose up -d --build
    echo "✅ Production режим запущен"
    echo "   Приложение:  http://localhost:8082"
    ;;
    
  *)
    echo "🛠  Управление режимом разработки Pyrus Tasks"
    echo ""
    echo "Использование: ./dev.sh [команда] [опции]"
    echo ""
    echo "Команды:"
    echo "  up          Запустить в режиме разработки"
    echo "  down        Остановить dev контейнеры"
    echo "  logs [srv]  Показать логи (опционально для конкретного сервиса)"
    echo "  ps          Показать статус контейнеров"
    echo "  restart     Перезапустить контейнеры"
    echo "  rebuild     Пересобрать и перезапустить"
    echo "  prod        Переключиться на production режим"
    echo ""
    echo "Примеры:"
    echo "  ./dev.sh up                 # Запустить dev режим"
    echo "  ./dev.sh logs backend       # Логи только backend"
    echo "  ./dev.sh restart frontend   # Перезапустить frontend"
    echo "  ./dev.sh prod               # Переключиться на production"
    ;;
esac

