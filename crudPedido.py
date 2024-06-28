from sqlalchemy.orm import Session
from datetime import datetime
import crudUsuario as usuario_service
import crudProducto as producto_service
from sqlalchemy.orm import Session
import models, schemas


def create_order(db: Session, order: schemas.PedidoCreate):
    db_order = models.Pedido(
        id_cliente=order.id_cliente,
        fecha_pedido=order.fecha_pedido,
        cantidad_productos=order.cantidad_productos,
        metodo_envio=order.metodo_envio,
        estado=order.estado
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order(db: Session, order_id: int):
    return db.query(models.Pedido).filter(models.Pedido.id_pedido == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Pedido).offset(skip).limit(limit).all()

def update_order(db: Session, order_id: int, order: schemas.PedidoUpdate):
    db_order = (db, order_id)
    if db_order is None:
        return None
    for key, value in order_id.dict().items():
        if value is not None:
            setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: int):
    db_order = get_order(db, order_id)
    if db_order is None:
        return None
    db.delete(db_order)
    db.commit()