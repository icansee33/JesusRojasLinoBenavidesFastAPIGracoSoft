from sqlalchemy.orm import Session
import models, schemas
from pydantic import Field


def get_user_by_email(db: Session, correo: str):
    print("Db: ", db, "Correo eléctronico: ", correo)
    return db.query(models.Usuario).filter(models.Usuario.correo_electronico == correo).first()

def get_user(db: Session, user_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id_usuario == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.contrasena + "notreallyhashed"
    db_user = models.Usuario(email=user.correo_electronico, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



"""

#Buscar item por su id
def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

#Buscar todos los items
def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

#Crear item
def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.model_dump())
    print("DB item: ", db_item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    print("Db items: ", db_item)
    return db_item

#Modificar item
def update_item(db: Session, item_id: int, item_update: schemas.ItemUpdate):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db_item.name = item_update.name
        db_item.description = item_update.description
        db.commit()
        db.refresh(db_item)
        print("Updated item: ", db_item)
        return db_item
    return None


#Delete item
def delete_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return db_item
    return None




"""