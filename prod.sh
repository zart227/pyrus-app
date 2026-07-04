#!/bin/bash

# Скрипт для управления production режимом

case "$1" in
  up)
    echo "🏭 Запуск в production режиме..."
    docker compose up -d --build
    echo ""
    echo "✅ Контейнеры запущены!"
    echo ""
    echo "📍 Доступ к приложению:"
    echo "   - Приложение (Nginx):      http://localhost:8082"
    echo "   - Backend API:             http://localhost:8000"
    echo "   - API документация:        http://localhost:8000/docs"
    echo "   - PostgreSQL:              localhost:5433"
    echo ""
    echo "📝 Команды:"
    echo "   Логи:           ./prod.sh logs"
    echo "   Остановить:     ./prod.sh down"
    echo "   Статус:         ./prod.sh ps"
    ;;
    
  down)
    echo "🛑 Остановка production контейнеров..."
    docker compose down
    echo "✅ Контейнеры остановлены"
    ;;
    
  logs)
    if [ -z "$2" ]; then
      echo "📋 Логи всех сервисов (Ctrl+C для выхода)..."
      docker compose logs -f
    else
      echo "📋 Логи сервиса: $2 (Ctrl+C для выхода)..."
      docker compose logs -f "$2"
    fi
    ;;
    
  ps)
    echo "📊 Статус контейнеров:"
    docker compose ps
    ;;
    
  restart)
    if [ -z "$2" ]; then
      echo "🔄 Перезапуск всех контейнеров..."
      docker compose restart
    else
      echo "🔄 Перезапуск сервиса: $2..."
      docker compose restart "$2"
    fi
    echo "✅ Перезапуск завершен"
    ;;
    
  rebuild)
    echo "🔨 Пересборка контейнеров..."
    docker compose up -d --build --force-recreate
    echo "✅ Пересборка завершена"
    ;;
    
  dev)
    echo "🛠 Переключение на dev режим..."
    docker compose down
    docker compose -f docker-compose.dev.yml up -d --build
    echo "✅ Dev режим запущен"
    echo "   Frontend (Vite dev):  http://localhost:8081"
    echo "   Приложение:           http://localhost:8082"
    ;;
    
  *)
    echo "🏭 Управление production режимом Pyrus Tasks"
    echo ""
    echo "Использование: ./prod.sh [команда] [опции]"
    echo ""
    echo "Команды:"
    echo "  up          Запустить в production режиме"
    echo "  down        Остановить контейнеры"
    echo "  logs [srv]  Показать логи (опционально для конкретного сервиса)"
    echo "  ps          Показать статус контейнеров"
    echo "  restart     Перезапустить контейнеры"
    echo "  rebuild     Пересобрать и перезапустить"
    echo "  dev         Переключиться на dev режим"
    echo ""
    echo "Примеры:"
    echo "  ./prod.sh up                # Запустить production режим"
    echo "  ./prod.sh logs backend      # Логи только backend"
    echo "  ./prod.sh restart nginx     # Перезапустить nginx"
    echo "  ./prod.sh dev               # Переключиться на dev"
    ;;
esac

