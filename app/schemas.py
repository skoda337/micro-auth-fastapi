from pydantic import BaseModel
from typing import List, Optional

# Схема для прав/ролей
class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int
    class Config:
        from_attributes = True

# Схема для пользователя
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    roles: List[Role] = []
    class Config:
        from_attributes = True