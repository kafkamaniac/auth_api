#Модели базы данных для API авторизации пользователей.

from peewee import Model, CharField, AutoField, DateTimeField
from app.database import db

class BaseModel(Model):
    """Базовая модель, связывающая модели с базой данных."""
    class Meta:
        database = db

class User(BaseModel):    
    """Модель пользователя, хранящая логин и хеш пароля."""
    id = AutoField()
    login = CharField(max_length=50, unique=True)
    hashed_password  = CharField(max_length=255)
    
    class Meta:
        table_name = "users"
        
