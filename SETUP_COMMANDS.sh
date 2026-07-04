#!/bin/bash

# Автоматическая настройка Nginx на хосте для доступа через /pyrus
# Использование: sudo ./SETUP_COMMANDS.sh

set -e

echo "🔧 Настройка Nginx для доступа к Pyrus Tasks через /pyrus"
echo ""

# Проверка прав sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Запустите скрипт с правами sudo: sudo ./SETUP_COMMANDS.sh"
    exit 1
fi

# Шаг 1: Установка Nginx
echo "📦 Шаг 1/4: Установка Nginx..."
if ! command -v nginx &> /dev/null; then
    apt update
    apt install -y nginx
    echo "✅ Nginx установлен"
else
    echo "✅ Nginx уже установлен"
fi

# Шаг 2: Копирование конфигурации
echo ""
echo "📝 Шаг 2/4: Копирование конфигурации..."
cp nginx-host.conf /etc/nginx/sites-available/pyrus
echo "✅ Конфигурация скопирована в /etc/nginx/sites-available/pyrus"

# Шаг 3: Активация конфигурации
echo ""
echo "🔗 Шаг 3/4: Активация конфигурации..."
if [ ! -L /etc/nginx/sites-enabled/pyrus ]; then
    ln -s /etc/nginx/sites-available/pyrus /etc/nginx/sites-enabled/pyrus
    echo "✅ Конфигурация активирована"
else
    echo "✅ Конфигурация уже активирована"
fi

# Шаг 4: Проверка и перезапуск Nginx
echo ""
echo "🔄 Шаг 4/4: Проверка и перезапуск Nginx..."
nginx -t
if [ $? -eq 0 ]; then
    systemctl restart nginx
    echo "✅ Nginx перезапущен"
else
    echo "❌ Ошибка в конфигурации Nginx"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Настройка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "   1. Запустите приложение: ./prod.sh up"
echo "   2. Откройте в браузере: http://$(hostname -I | awk '{print $1}')/pyrus/"
echo ""
echo "📝 Управление:"
echo "   ./prod.sh logs    - Просмотр логов"
echo "   ./prod.sh ps      - Статус контейнеров"
echo "   ./prod.sh down    - Остановка"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

