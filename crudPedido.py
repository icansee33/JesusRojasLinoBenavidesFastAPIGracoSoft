from sqlalchemy.orm import Session
from datetime import datetime
import crudUsuario as usuario_service
import crudProducto as producto_service
from sqlalchemy.orm import Session
import models, schemas


def create_order(db: Session, order: schemas.PedidoCreate):
    db_order = models.Pedido(
        cedula_identidad=order.cedula_identidad,
        id_producto=order.id_producto,
        fecha_pedido=order.fecha_pedido,
        cantidad_productos=order.cantidad_productos,
        metodo_envio=order.metodo_envio,
        monto_total=order.monto_total,
        estado=order.estado
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order_by_id(db: Session, order_id: int):
    return db.query(models.Pedido).filter(models.Pedido.id_pedido == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Pedido).offset(skip).limit(limit).all()

def update_order(db: Session, order_id: int, order: schemas.PedidoUpdate):
    db_order = get_order_by_id(db, order_id)   
    if db_order is None:
        for key, value in order.dict().items():
            if value is not None:
                setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
    return db_order


def get_orders_product(db: Session):
    return db.query(models.Pedido, models.Producto).join(models.Producto, models.Pedido.id_producto == models.Producto.id_producto).all()


def cancel_order(db: Session, order_id: int):
    db_order = get_order_by_id(db, order_id)
    if db_order is None:
        return None
    db.delete(db_order)
    db.commit()
    return db_order
