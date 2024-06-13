from sqlalchemy.orm import Session
import models, schemas
from pydantic import Field



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
