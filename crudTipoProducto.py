from sqlalchemy.orm import Session
import models, schemas

def create_type_product(db: Session, product: schemas.TipoCreate):
    db_type = models.Tipo_Producto(
        nombre=product.nombre
    )
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

def get_type_by_name(db: Session, type_id: int):
    return db.query(models.Tipo_Producto).filter(models.Tipo_Producto.nombre == type_id).first()


