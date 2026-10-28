#Хэширование паролей и создание JWT токенов для аутентификации пользователей.

from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.database import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:    
    """Хеширует пароль перед сохранением в базе данных."""
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:    
    """Проверяет пароль, сравнивая его с сохранённым хешем."""
    return password_hash.verify(password, hashed_password)

def create_access_token(user_id: int) -> str:    
    """Создаёт короткоживущий JWT-токен доступа для пользователя."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: int) -> str:
    """Создаёт долгоживущий JWT-токен обновления для пользователя."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def get_user_id_from_token(token: str, expected_type: str) -> int:
    """Извлекает идентификатор пользователя из JWT-токена."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") == expected_type:
            return int(payload.get("sub"))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        pass
    return None
