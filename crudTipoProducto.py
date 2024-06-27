from sqlalchemy.orm import Session
import models, schemas

def create_type_product(db: Session, type_product: schemas.TypeCreate):
    db_type = models.Tipo_Producto(
        nombre=type_product.nombre
    )
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

def get_type_by_id(db: Session, type_id: int):
    return db.query(models.Tipo_Producto).filter(models.Tipo_Producto.id_tipo == type_id).first()

def update_type_product(db: Session, type_id: int, type: schemas.TypeUpdate):
    db_type = get_type_by_id(db, type_id)
    if db_type is None:
        return None
    for key, value in type.dict().items():
        if value:
            setattr(db_type, key, value)
    db.commit()
    db.refresh(db_type)
    return db_type

def delete_type_product(db: Session, type_id: int):
    db_type = get_type_by_id(db, type_id)
    if db_type is None:
        return None
    db.delete(db_type)
    db.commit()
    return db_type

def get_types(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tipo_Producto).offset(skip).limit(limit).all()
