from sqlalchemy.orm import Session
from datetime import datetime
import crudUsuario as usuario_service
import crudProducto as producto_service
from sqlalchemy.orm import Session
import models, schemas

def create_pedido(db: Session, pedido: schemas.PedidoCreate):
    db_pedido = models.Pedido(
        id_cliente=pedido.id_cliente,
        fecha_pedido=pedido.fecha_pedido,
        cantidad_productos=pedido.cantidad_productos,
        metodo_env=pedido.metodo_env,
        estado=pedido.estado
    )
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)
    return db_pedido

def get_pedido(db: Session, pedido_id: int):
    return db.query(models.Pedido).filter(models.Pedido.id_pedido == pedido_id).first()

def get_pedidos(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Pedido).offset(skip).limit(limit).all()

def update_pedido(db: Session, pedido_id: int, pedido: schemas.PedidoUpdate):
    db_pedido = get_pedido(db, pedido_id)
    if db_pedido is None:
        return None
    for key, value in pedido.dict().items():
        if value is not None:
            setattr(db_pedido, key, value)
    db.commit()
    db.refresh(db_pedido)
    return db_pedido

def delete_pedido(db: Session, pedido_id: int):
    db_pedido = get_pedido(db, pedido_id)
    if db_pedido is None:
        return None
    db.delete(db_pedido)
    db.commit()