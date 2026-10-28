#Pydantic-схемы для проверки запросов и формирования ответов API.

from pydantic import BaseModel, Field

class UserRegister(BaseModel):    
    """Данные для регистрации нового пользователя."""
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=255)
    
class UserLogin(BaseModel):    
    """Данные для авторизации пользователя."""
    login: str = Field(..., min_length=3, max_length=50)
    password: str
    
class UserResponse(BaseModel):
    """Ответ с данными пользователя."""
    id: int
    login: str


class TokenResponse(BaseModel):
    """Ответ с токенами доступа и обновления."""
    access_token: str    
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    """Запрос на обновление токенов с использованием Refresh Token."""
    refresh_token: str
    
class UpdatePassword(BaseModel):
    """Запрос на обновление пароля пользователя."""
    old_password: str = Field(..., min_length=8, max_length=255)
    new_password: str = Field(..., min_length=8, max_length=255)
    
class UpdateLogin(BaseModel):
    """Запрос на обновление логина пользователя."""
    new_login: str = Field(..., min_length=3, max_length=50)