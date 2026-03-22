from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Access Control System")

# Эндпоинт для создания роли
@app.post("/roles/", response_model=schemas.Role)
def create_role(role: schemas.RoleCreate, db: Session = Depends(database.get_db)):
    db_role = models.Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# Эндпоинт для получения списка всех ролей
@app.get("/roles/", response_model=List[schemas.Role])
def get_roles(db: Session = Depends(database.get_db)):
    return db.query(models.Role).all()

# Получить список всех пользователей и их ролей
@app.get("/users/", response_model=List[schemas.User])
def get_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users


# Эндпоинт для регистрации нового пользователя
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Проверка, нет ли уже такого имени в базе
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=user.password  # В реальных проектах тут делают хеширование!
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Эндпоинт-связка: присваиваем роль пользователю
@app.post("/users/{user_id}/roles/{role_id}")
def assign_role_to_user(user_id: int, role_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    role = db.query(models.Role).filter(models.Role.id == role_id).first()

    if not user or not role:
        raise HTTPException(status_code=404, detail="User or Role not found")

    # Магия SQLAlchemy: просто добавляем объект роли в список ролей юзера
    user.roles.append(role)
    db.commit()
    return {"message": f"Role {role.name} assigned to user {user.username}"}

# Удаление пользователя
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}