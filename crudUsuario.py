from sqlalchemy.orm import Session
import models, schemas
from pydantic import Field
from passlib.context import CryptContext
from schemas import Respuesta, Token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(db: Session, user: schemas.UserCreate):
        db_user = models.Usuario(
        nombre=user.nombre,
        apellido=user.apellido,
        cedula_identidad=user.cedula_identidad,
        fecha_nacimiento=user.fecha_nacimiento,
        direccion=user.direccion,
        correo_electronico=user.correo_electronico,
        contrasena= get_password_hash(user.contrasena), 
        tipo_usuario=user.tipo_usuario
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        real_user = schemas.User(
        nombre=db_user.nombre,
        apellido=db_user.apellido,
        cedula_identidad=db_user.cedula_identidad,
        fecha_nacimiento=db_user.fecha_nacimiento,
        direccion=db_user.direccion,
        correo_electronico=db_user.correo_electronico,
        contrasena=db_user.contrasena,  
        tipo_usuario=user.tipo_usuario
        )
        respuesta = Respuesta[schemas.User](
            ok=True, 
            mensaje='Usuario registrado exitósamente. ADVERTENCIA: ESTA ES LA ÚLTIMA VEZ QUE VERÁ SU CONTRASEÑA LIBREMENTE', 
            data=real_user
        )
        return respuesta            


def buscar_usuario(db: Session, user_id: str): 
    user_return = db.query(models.Usuario).filter(models.Usuario.cedula_identidad == user_id).first()

    if user_return == None:
        return Respuesta[schemas.User](ok=False, mensaje='Usuario no encontrado')

    user = schemas.User(
        nombre=user_return.nombre,
        apellido=user_return.apellido,
        cedula_identidad=user_return.cedula_identidad,
        fecha_nacimiento=user_return.fecha_nacimiento,
        direccion=user_return.direccion,
        correo_electronico=user_return.correo_electronico,
        contrasena=user_return.contrasena,  
        tipo_usuario=user_return.tipo_usuario
    )
    
    return Respuesta[schemas.User](ok=True, mensaje='Usuario encontrado', data=user)


def get_user_by_email(db: Session, email: str):
    print("Get email: ", email)
    return db.query(models.Usuario).filter(models.Usuario.correo_electronico == email).first()


def get_user_by_ci(db: Session, user_id: int):
    return db.query(models.Usuario).filter(models.Usuario.cedula_identidad == user_id).first()


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user_by_ci(db, user_id)
    if db_user is None:
        return None
    for key, value in user.dict().items():
        if value:
            if key == 'contrasena':
                setattr(db_user, key, get_password_hash(value))
            else:
                setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user_by_ci(db, user_id)
    if db_user is None:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

def obtener_usuario(db: Session, user_id: str):
    return db.query(models.Usuario).filter(models.Usuario.cedula_identidad == user_id).first()
