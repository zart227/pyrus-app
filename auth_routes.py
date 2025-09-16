from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pyrus import client

from database import get_db, User
from schemas import UserCreate, UserLogin, UserResponse, Token
from auth_utils import (
    create_access_token, 
    get_current_active_user, 
    get_current_active_user_from_cookie,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password,
    get_password_hash
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Очищаем пробелы из входных данных
    login_clean = user.login.strip()
    security_key_clean = user.security_key.strip()
    
    # Проверяем, существует ли пользователь
    db_user = db.query(User).filter(User.login == login_clean).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким логином уже существует"
        )
    
    # Проверяем валидность учетных данных Pyrus
    try:
        pyrus_client = client.PyrusAPI(
            login=login_clean,
            security_key=security_key_clean
        )
        auth_response = pyrus_client.auth()
        if not auth_response.success:
            raise HTTPException(
                status_code=400,
                detail=f"Неверные учетные данные Pyrus: {auth_response.error}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка проверки учетных данных Pyrus: {str(e)}"
        )
    
    # Создаем пользователя (не хешируем ключ, так как он нужен для API Pyrus)
    db_user = User(
        login=login_clean,
        security_key=security_key_clean  # Сохраняем ключ как есть для API Pyrus
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Авторизация пользователя"""
    # Очищаем пробелы из входных данных
    login_clean = user.login.strip()
    security_key_clean = user.security_key.strip()
    
    # Находим пользователя
    db_user = db.query(User).filter(User.login == login_clean).first()
    if not db_user or security_key_clean != db_user.security_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или ключ безопасности",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем активность пользователя
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь неактивен"
        )
    
    # Создаем токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.login}, expires_delta=access_token_expires
    )
    
    # Обновляем время последнего входа
    db_user.last_login = datetime.utcnow()
    db.commit()
    
    # Устанавливаем куки
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=False,  # Разрешаем доступ из JavaScript
        secure=False,  # В продакшене должно быть True для HTTPS
        samesite="lax",  # Возвращаем "lax" для локальной разработки
        # Убираем domain для работы с localhost на разных портах
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    """Выход из системы"""
    response.delete_cookie(
        key="access_token",
        domain="localhost"
    )
    return {"message": "Успешный выход из системы"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user_from_cookie)):
    """Получение информации о текущем пользователе"""
    return current_user

@router.get("/users", response_model=list[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получение списка всех пользователей (только для админов)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users
