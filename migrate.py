#!/usr/bin/env python3
"""
Скрипт для создания миграций Alembic
"""
import os
import sys
from alembic.config import Config
from alembic import command

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def init_alembic():
    """Инициализация Alembic"""
    alembic_cfg = Config("alembic.ini")
    command.init(alembic_cfg, "alembic")

def create_migration(message="Initial migration"):
    """Создание миграции"""
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, message=message, autogenerate=True)

def upgrade_database():
    """Применение миграций"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python migrate.py init          - Инициализация Alembic")
        print("  python migrate.py create <msg>   - Создание миграции")
        print("  python migrate.py upgrade        - Применение миграций")
        sys.exit(1)
    
    command_arg = sys.argv[1]
    
    if command_arg == "init":
        init_alembic()
        print("✓ Alembic инициализирован")
    elif command_arg == "create":
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto migration"
        create_migration(message)
        print(f"✓ Миграция '{message}' создана")
    elif command_arg == "upgrade":
        upgrade_database()
        print("✓ Миграции применены")
    else:
        print(f"Неизвестная команда: {command_arg}")
        sys.exit(1)
