"""from sqlalchemy.orm import Session
import models, schemas
from pydantic import Field
from passlib.context import CryptContext

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
        contrasena=get_password_hash(user.contrasena),
        tipo_usuario=user.tipo_usuario
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


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
    return db_user"""


from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obtener_hash_contrasena(password):
    return pwd_context.hash(password)

def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    db_usuario = models.Usuario(
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        cedula_identidad=usuario.cedula_identidad,
        fecha_nacimiento=usuario.fecha_nacimiento,
        direccion=usuario.direccion,
        correo_electronico=usuario.correo_electronico,
        contrasena=obtener_hash_contrasena(usuario.contrasena),
        tipo_usuario=usuario.tipo_usuario
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def obtener_usuario_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.correo_electronico == email).first()

def obtener_usuario_por_ci(db: Session, user_id: int):
    return db.query(models.Usuario).filter(models.Usuario.cedula_identidad == user_id).first()

def actualizar_usuario(db: Session, user_id: int, usuario: schemas.UsuarioActualizar):
    db_usuario = obtener_usuario_por_ci(db, user_id)
    if db_usuario is None:
        return None
    for key, value in usuario.dict().items():
        if value:
            if key == 'contrasena':
                setattr(db_usuario, key, obtener_hash_contrasena(value))
            else:
                setattr(db_usuario, key, value)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def eliminar_usuario(db: Session, user_id: int):
    db_usuario = obtener_usuario_por_ci(db, user_id)
    if db_usuario is None:
        return None
    db.delete(db_usuario)
    db.commit()
    return db_usuario
