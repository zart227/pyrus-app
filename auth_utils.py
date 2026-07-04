from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os

from database import get_db, User
from schemas import TokenData

# Настройки для JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Настройки для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройки для Bearer токенов
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT access-токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Создание JWT refresh-токена"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Установка кук авторизации"""
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=False,
        secure=False,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )

def clear_auth_cookies(response: Response):
    """Удаление кук авторизации"""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")

def get_refresh_token_from_cookie(request: Request) -> Optional[str]:
    """Получение refresh-токена из куки"""
    return request.cookies.get("refresh_token")

def verify_refresh_token(token: str, credentials_exception):
    """Проверка JWT refresh-токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        return TokenData(login=login)
    except JWTError:
        raise credentials_exception

def verify_token(token: str, credentials_exception):
    """Проверка JWT токена"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type not in (None, "access"):
            raise credentials_exception
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = TokenData(login=login)
    except JWTError:
        raise credentials_exception
    return token_data

def get_token_from_cookie(request: Request) -> Optional[str]:
    """Получение токена из куки"""
    access_token = request.cookies.get("access_token")
    if access_token:
        # Убираем "Bearer " префикс если есть
        if access_token.startswith("Bearer "):
            return access_token[7:]
        return access_token
    return None

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Получение текущего пользователя из куки"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = get_token_from_cookie(request)
    if not token:
        raise credentials_exception
    
    token_data = verify_token(token, credentials_exception)
    
    user = db.query(User).filter(User.login == token_data.login).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = verify_token(token, credentials_exception)
    
    user = db.query(User).filter(User.login == token_data.login).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Получение активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_user_from_cookie(current_user: User = Depends(get_current_user_from_cookie)):
    """Получение активного пользователя из куки"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
