from sqlalchemy.orm import Session
import models, schemas

def create_calificacion(db: Session, calificacion: schemas.CalificacionCreate):
    db_calificacion = models.Calificacion(
        id_producto=calificacion.id_producto,
        id_cliente=calificacion.id_cliente,
        calificacion=calificacion.calificacion,
        comentario=calificacion.comentario
    )
    db.add(db_calificacion)
    db.commit()
    db.refresh(db_calificacion)
    return db_calificacion

def get_calificaciones_by_producto(db: Session, producto_id: int):
    return db.query(models.Calificacion).filter(models.Calificacion.id_producto == producto_id).all()