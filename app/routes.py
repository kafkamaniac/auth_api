#Маршруты API для регистрации, авторизации и управления пользователями.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from peewee import IntegrityError

from app.models import User
from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse, UpdatePassword, UpdateLogin, RefreshRequest
from app.security import hash_password, verify_password, create_access_token, get_user_id_from_token, create_refresh_token

router = APIRouter(prefix="/api")
bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> User:    
    """Проверяет токен доступа и возвращает текущего пользователя."""
    try:
        user_id = get_user_id_from_token(credentials.credentials, "access")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = User.get_or_none(User.id == user_id)
    if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister):
    """Регистрирует пользователя и сохраняет хэш пароля."""
    if User.select().where(User.login == user.login).exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login already exists")
    
    user = User.create(login=user.login, hashed_password=hash_password(user.password))
    
    return user

@router.post("/auth/login", response_model=TokenResponse)
def login_user(user: UserLogin):    
    """Проверяет учётные данные и выдаёт Access и Refresh токены."""
    db_user = User.get_or_none(User.login == user.login)
    if db_user is None or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or password", headers={"WWW-Authenticate": "Bearer"}    )
    
    access_token = create_access_token(db_user.id)
    refresh_token = create_refresh_token(db_user.id)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/auth/refresh", response_model=TokenResponse)
def refresh_token(refresh_request: RefreshRequest):    
    """Проверяет Refresh Token и выдаёт новую пару токенов."""
    try:
        user_id = get_user_id_from_token(refresh_request.refresh_token, expected_type= "refresh")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    db_user = User.get_or_none(User.id == user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    access_token = create_access_token(db_user.id)
    refresh_token = create_refresh_token(db_user.id)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: User = Depends(get_current_user)):    
    """Возвращает данные текущего пользователя, если ID совпадает."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return current_user

@router.delete("/user/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    """Удаляет пользователя, если ID совпадает."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    User.delete().where(User.id == user_id).execute()
    return {"detail": "User deleted"}

@router.put("/auth/update_password")
def update_password(update: UpdatePassword, current_user: User = Depends(get_current_user)):
    """Обновляет пароль пользователя, если старый пароль совпадает."""
    if not verify_password(update.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    
    current_user.hashed_password = hash_password(update.new_password)
    current_user.save()
    
    return {"detail": "Password updated successfully"}

@router.put("/user/{user_id}", response_model=UserResponse)
def update_login(user_id: int, update: UpdateLogin, current_user: User = Depends(get_current_user)):
    """Обновляет логин пользователя, если ID совпадает."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if User.select().where(User.login == update.new_login).exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login already exists")

    current_user.login = update.new_login
    current_user.save()
    
    return current_user

