from sqlalchemy.orm import Session
from datetime import datetime
import crudUsuario as usuario_service
import crudProducto as producto_service
from sqlalchemy.orm import Session
import models, schemas


def create_charge(db: Session, charge: schemas.ChargeCreate):
    db_order = models.Pedido(
        id_producto=charge.id_producto,
        cedula_identidad=charge.cedula_identidad,
        descripcion_encargo=charge.descripcion_encargo,
        fecha_encargo=charge.fecha_encargo,
        cantidad_productos= charge.cantidad_productos,
        metodo_envio=charge.metodo_envio,
        estado=charge.estado_encargo
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_charge_by_id(db: Session, charge_id: int):
    return db.query(models.Encargo).filter(models.Encargo.id_encargo == charge_id).first()


def get_charge(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Encargo).offset(skip).limit(limit).all()


def update_charge(db: Session, charge_id: int, charge: schemas.ChargeUpdate):
    db_charge = (db, charge_id)
    if db_charge is None:
        return None
    for key, value in charge_id.dict().items():
        if value is not None:
            setattr(db_charge, key, value)
    db.commit()
    db.refresh(db_charge)
    return db_charge


def delete_charge(db: Session, charge_id: int):
    db_charge = get_charge_by_id(db, charge_id)
    if db_charge is None:
        return None
    db.delete(db_charge)
    db.commit()