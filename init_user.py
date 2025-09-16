#!/usr/bin/env python3
"""
Скрипт для инициализации первого пользователя из переменных окружения
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from pyrus import client

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, User, SessionLocal

def init_first_user():
    """Инициализация первого пользователя из .env файла"""
    load_dotenv()
    
    login = os.getenv("PYRUS_LOGIN")
    security_key = os.getenv("PYRUS_SECURITY_KEY")
    
    if not login or not security_key:
        print("Ошибка: PYRUS_LOGIN и PYRUS_SECURITY_KEY должны быть установлены в .env файле")
        return False
    
    # Проверяем валидность учетных данных
    try:
        pyrus_client = client.PyrusAPI(login=login, security_key=security_key)
        auth_response = pyrus_client.auth()
        if not auth_response.success:
            print(f"Ошибка проверки учетных данных Pyrus: {auth_response.error}")
            return False
        print("✓ Учетные данные Pyrus валидны")
    except Exception as e:
        print(f"Ошибка проверки учетных данных Pyrus: {str(e)}")
        return False
    
    # Создаем сессию базы данных
    db = SessionLocal()
    
    try:
        # Проверяем, существует ли уже пользователь
        existing_user = db.query(User).filter(User.login == login).first()
        if existing_user:
            print(f"Пользователь {login} уже существует в базе данных")
            return True
        
        # Создаем нового пользователя
        user = User(
            login=login,
            security_key=security_key,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✓ Пользователь {login} успешно создан в базе данных")
        print(f"ID пользователя: {user.id}")
        return True
        
    except Exception as e:
        print(f"Ошибка создания пользователя: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Инициализация первого пользователя...")
    success = init_first_user()
    if success:
        print("✓ Инициализация завершена успешно")
        sys.exit(0)
    else:
        print("✗ Ошибка инициализации")
        sys.exit(1)
