from sqlalchemy.orm import Session
import models, schemas
#
def create_type_product(db: Session, product: schemas.TipoCreate):
    db_type = models.Tipo_Producto(
        nombre=product.nombre
    )
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

def get_type_by_id(db: Session, type_id: int):
    return db.query(models.Tipo_Producto).filter(models.Tipo_Producto.id_tipo == type_id).first()


def update_type_product(db: Session, id_tipo: int, type: schemas.TipoUpdate):
    db_type= get_type_by_id(db, id_tipo)
    if db_type is None:
        return None
    for key, value in type.dict().items():
        if value:
            setattr(db_type, key, value)
    db.commit()
    db.refresh(db_type)

def delete_type_product(db: Session, id_tipo: int):
    db_type = get_type_by_id(db, id_tipo)
    if db_type is None:
        return None
    db.delete(db_type)
    db.commit()
    return db_type
