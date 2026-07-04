#!/bin/bash

# Скрипт для обновления конфигурации Nginx с редиректом

echo "🔧 Обновление конфигурации Nginx..."
echo ""

# Проверка прав sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Запустите скрипт с правами sudo: sudo ./fix_nginx_redirect.sh"
    exit 1
fi

# Копируем обновленную конфигурацию
echo "📝 Копируем обновленную конфигурацию..."
cp nginx-host.conf /etc/nginx/sites-available/pyrus
echo "✅ Конфигурация обновлена"

# Проверяем конфигурацию
echo ""
echo "📝 Проверяем конфигурацию..."
nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Конфигурация корректна"
else
    echo "❌ Ошибка в конфигурации Nginx"
    exit 1
fi

# Перезагружаем Nginx
echo ""
echo "📝 Перезагружаем Nginx..."
systemctl reload nginx
echo "✅ Nginx перезагружен"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Готово! Теперь при обращении к http://$(hostname -I | awk '{print $1}')/"
echo "   вы будете автоматически перенаправлены на /pyrus/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

