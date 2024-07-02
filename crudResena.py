from sqlalchemy.orm import Session
import models, schemas

def get_resenas(db: Session):
    return db.query(models.Resena).all()

def get_resena_by_id(db: Session, review_id: int):
    return db.query(models.Resena).filter(models.Resena.id_resena == review_id).first()

def create_resena(db: Session, review: schemas.ReviewCreate):
    db_review = models.Resena(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def update_resena(db: Session, review_id: int, review: schemas.ReviewUpdate):
    db_review = db.query(models.Resena).filter(models.Resena.id_resena == review_id).first()
    if db_review:
        for key, value in review.dict().items():
            setattr(db_review, key, value)
        db.commit()
        db.refresh(db_review)
    return db_review

def delete_resena(db: Session, review_id: int):
    db_review = db.query(models.Resena).filter(models.Resena.id_resena == review_id).first()
    if db_review:
        db.delete(db_review)
        db.commit()
    return db_review
