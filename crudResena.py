from sqlalchemy.orm import Session
import models, schemas

def create_resena(db: Session, resena: schemas.ReviewCreate):
    db_resena = models.Resena(
        id_producto=resena.id_producto,
        fecha_inversion=resena.fecha_inversion,
        creador=resena.creador,
        anios_produccion=resena.anios_produccion,
        anecdotas=resena.anecdotas
    )
    db.add(db_resena)
    db.commit()
    db.refresh(db_resena)
    return db_resena

def get_resena_by_id(db: Session, resena_id: int):
    return db.query(models.Resena).filter(models.Resena.id_resena == resena_id).first()

def get_resenas_by_producto(db: Session, producto_id: int):
    return db.query(models.Resena).filter(models.Resena.id_producto == producto_id).all()

def update_resena(db: Session, resena_id: int, resena: schemas.ReviewUpdate):
    db_resena = get_resena_by_id(db, resena_id)
    if db_resena is None:
        return None
    for key, value in resena.dict().items():
        if value is not None:
            setattr(db_resena, key, value)
    db.commit()
    db.refresh(db_resena)
    return db_resena

def delete_resena(db: Session, resena_id: int):
    db_resena = get_resena_by_id(db, resena_id)
    if db_resena is None:
        return None
    db.delete(db_resena)
    db.commit()
    return db_resena