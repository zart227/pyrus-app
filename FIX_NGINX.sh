#!/bin/bash

# Скрипт для исправления конфликта с дефолтной конфигурацией Nginx

echo "🔧 Исправление конфигурации Nginx..."
echo ""

# Проверка прав sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Запустите скрипт с правами sudo: sudo ./FIX_NGINX.sh"
    exit 1
fi

# Шаг 1: Удаляем дефолтную конфигурацию
echo "📝 Шаг 1: Удаляем дефолтную конфигурацию Nginx..."
if [ -L /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
    echo "✅ Дефолтная конфигурация удалена"
else
    echo "ℹ️  Дефолтная конфигурация уже удалена"
fi

# Шаг 2: Копируем обновленную конфигурацию
echo ""
echo "📝 Шаг 2: Обновляем конфигурацию pyrus..."
cp nginx-host.conf /etc/nginx/sites-available/pyrus
echo "✅ Конфигурация обновлена"

# Шаг 3: Проверяем конфигурацию
echo ""
echo "📝 Шаг 3: Проверяем конфигурацию..."
nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Конфигурация корректна"
else
    echo "❌ Ошибка в конфигурации Nginx"
    exit 1
fi

# Шаг 4: Перезагружаем Nginx
echo ""
echo "📝 Шаг 4: Перезагружаем Nginx..."
systemctl reload nginx
echo "✅ Nginx перезагружен"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Готово! Теперь попробуйте открыть:"
echo "   http://$(hostname -I | awk '{print $1}')/pyrus/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

