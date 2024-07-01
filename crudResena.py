from sqlalchemy.orm import Session
import models, schemas

def create_resena(db: Session, review: schemas.ReviewCreate):
    db_review = models.Resena(
        id_producto=review.id_producto,
        fecha_invencion=review.fecha_invencion,
        creador=review.creador,
        anios_produccion=review.anios_produccion,
        anecdotas=review.anecdotas
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_resena_by_id(db: Session, review_id: int):
    return db.query(models.Resena).filter(models.Resena.id_resena == review_id).first()

def update_resena(db: Session, review_id: int, resena: schemas.ReviewUpdate):
    db_review = get_resena_by_id(db, review_id)
    if db_review is None:
        return None
    for key, value in resena.dict().items():
        if value is not None:
            setattr(db_review, key, value)
    db.commit()
    db.refresh(db_review)
    return db_review

def delete_resena(db: Session, review_id: int):
    db_review = get_resena_by_id(db, review_id)
    if db_review is None:
        return None
    db.delete(db_review)
    db.commit()
    return db_review

def get_resenas(db: Session, skip: int = 10, limit: int = 100):
    return db.query(models.Resena).offset(skip).limit(limit).all()