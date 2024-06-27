from sqlalchemy.orm import Session
from datetime import datetime
from schemas import Respuesta
import compras.models as models
import compras.schemas as schemas
import crudUsuario as usuario_service
import crudProducto as producto_service
import tipo_Compra.crud as tipo_compra_service

def realizar_compra(db: Session, compra: schemas.CompraCrear):

    respuesta_usuario = usuario_service.buscar_usuario(db=db, cedula=compra.cliente_cedula)
    if not respuesta_usuario.ok:
        return Respuesta[schemas.Compra](ok=False, mensaje='cedula inexistente, porfavor intentelo de nuevo')

    respuesta_producto = producto_service.get_producto(db=db, id=compra.producto_id)
    if not respuesta_producto.ok:
        return Respuesta[schemas.Compra](ok=False, mensaje='Producto inexistente')

    respuesta_tipo_compra = tipo_compra_service.get_tipo_compra(db=db, id=compra.tipo_compra_id)
    if not respuesta_tipo_compra.ok:
        return Respuesta[schemas.Compra](ok=False, mensaje='Tipo de compra inexistente')

    db_compra = models.Compra(
        cantidad=compra.cantidad, 
        fecha=datetime.now, 
        cliente_cedula=compra.cliente_cedula, 
        producto_id=compra.producto_id, 
        tipo_compra_id=compra.tipo_compra_id, 
        estado_compra_id=1)
    db.add(db_compra)
    db.commit()
    db.refresh(db_compra)

    compra = schemas.Compra(id=db_compra.id, 
                            cantidad=db_compra.cantidad, 
                            cliente_cedula=db_compra.cliente_cedula, 
                            producto_id=db_compra.id, 
                            tipo_compra_id=db_compra.tipo_compra_id, 
                            estado_compra_id=db_compra.estado_compra_id) 
    respuesta = Respuesta[schemas.Compra](ok=True, mensaje='Compra realizada', data=compra)
    return respuesta


def aprobar_compra(db: Session, id_compra: int):

    compra_found = db.query(models.Compra).filter(models.Compra.id == id_compra).first()

    if compra_found == None:
        return Respuesta[schemas.Compra](ok=False, mensaje='Al parecer no podemos aprobar su compra, porfavor verifique que exista')
    compra_found.estado_compra_id = 2
    db.commit()
    return Respuesta[schemas.Compra](ok=True, mensaje='La compra fue aprobada exitosamente')


def rechazar_compra(db: Session, id_compra: int):
    compra_found = db.query(models.Compra).filter(models.Compra.id == id_compra).first()

    if compra_found == None:
        return Respuesta[schemas.Compra](ok=False, mensaje='La compra que desea rechazar no existe')
    compra_found.estado_compra_id = 3
    db.commit()
    return Respuesta[schemas.Compra](ok=True, mensaje='La compra fue rechazada exitosamente')

def listar_compras(db: Session): 
    return db.query(models.Compra).all()

def get_compra(db: Session, id: int):
    returned = db.query(models.Compra).filter(models.Compra.id == id).first()
    if returned == None:
        return Respuesta[schemas.Compra](ok=False, mensaje='La compra no pudo ser encontrada')
    compra = schemas.Compra(id=returned.id, 
                            cantidad=returned.cantidad, 
                            cliente_cedula=returned.cliente_cedula, 
                            producto_id=returned.id, 
                            tipo_compra_id=returned.tipo_compra_id, 
                            estado_compra_id=returned.estado_compra_id) 
    return Respuesta[schemas.Compra](ok=True, mensaje='Compra encontrada', data=compra)


def modificar_compra(db: Session, id: int, compra: schemas.CompraCrear): 
    lista = db.query(models.Compra).all()
    for este in lista: 
        if este.id == id: 
            este.cantidad = compra.cantidad
            este.fecha = compra.fecha
            este.cliente_cedula = compra.cliente_cedula
            este.producto_id = compra.producto_id
            este.tipo_compra_id = compra.tipo_compra_id
            este.estado_compra_id = compra.estado_compra_id
            break
    db.commit()
    return este

def eliminar_compra(db: Session, id: int): 
    compra = db.query(models.Compra).filter(models.Compra.id == id).first()
    db.delete(compra)
    db.commit()
    return compra