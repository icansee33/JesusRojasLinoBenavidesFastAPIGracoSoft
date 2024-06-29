from sqlalchemy.orm import Session
import models, schemas

def create_detalle_pedido(db: Session, detalle_pedido: schemas.DetallePedidoCreate):
    db_detalle_pedido = models.DetallePedido(
        id_pedido=detalle_pedido.id_pedido,
        id_producto=detalle_pedido.id_producto,
        cantidad=detalle_pedido.cantidad,
        precio_unitario=detalle_pedido.precio_unitario
    )
    db.add(db_detalle_pedido)
    db.commit()
    db.refresh(db_detalle_pedido)
    return db_detalle_pedido

def get_detalle_pedido(db: Session, detalle_id: int):
    return db.query(models.DetallePedido).filter(models.DetallePedido.id_detalle == detalle_id).first()

def get_detalles_pedido(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.DetallePedido).offset(skip).limit(limit).all()

def update_detalle_pedido(db: Session, detalle_id: int, detalle_pedido: schemas.DetallePedidoUpdate):
    db_detalle_pedido = get_detalle_pedido(db, detalle_id)
    if db_detalle_pedido is None:
        return None
    for key, value in detalle_pedido.dict().items():
        if value is not None:
            setattr(db_detalle_pedido, key, value)
    db.commit()
    db.refresh(db_detalle_pedido)
    return db_detalle_pedido

def delete_detalle_pedido(db: Session, detalle_id: int):
    db_detalle_pedido = get_detalle_pedido(db, detalle_id)
    if db_detalle_pedido is None:
        return None
    db.delete(db_detalle_pedido)
    db.commit()
