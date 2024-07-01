<<<<<<< HEAD
from sqlalchemy.orm import Session
from typing import Union, Any
from datetime import timedelta, datetime, timezone
from jose import jwt
from schemas import Respuesta, Token
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import models
import schemas
=======
"""from sqlalchemy.orm import Session
import models, schemas
from pydantic import Field
>>>>>>> 63a0bbf7860884724fbd5f7b8f18ce118d65d58a
from passlib.context import CryptContext
from usuarios.exceptions import LoginExpired, RequiresLoginException

class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "27A0D7C4CCCE76E6BE39225B7EEE8BD0EF890DE82D49E459F4C405C583080AB0"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=self.ALGORITHM)
            return payload
        except jwt.ExpiredSignatureError:
            raise LoginExpired()
        except jwt.JWTError as e:
            raise RequiresLoginException()
    
    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def get_hash_password(self, plain_password):
        return self.pwd_context.hash(plain_password)

    def verify_password(self, plain_password, hash_password):
        return self.pwd_context.verify(plain_password, hash_password)

    async def authenticate_user(self, db: Session, cedula: str, contraseña: str):
        try:
            usuario = obtener_usuario(db, cedula)
            if usuario: 
                password_check = self.verify_password(contraseña, usuario.contraseña)
                if password_check: 
                    return usuario
                else: 
                    return False
            else: 
                return False
        except:
            raise RequiresLoginException()

    def registrar_usuario(self, db: Session, usuario: schemas.UsuarioCrear):
        db_usuario = models.Usuario(
            cedula=usuario.cedula, 
            nombres=usuario.nombres, 
            apellidos=usuario.apellidos, 
            direccion=usuario.direccion, 
            nacimiento=usuario.nacimiento, 
            correo=usuario.correo, 
            contraseña=self.get_hash_password(usuario.contraseña), 
            tipo_id=usuario.tipo_id
        )
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        actual = schemas.Usuario(
            cedula=db_usuario.cedula, 
            nombres=db_usuario.nombres, 
            apellidos=db_usuario.apellidos, 
            direccion=db_usuario.direccion, 
            nacimiento=db_usuario.nacimiento, 
            correo=db_usuario.correo, 
            contraseña=usuario.contraseña, 
            tipo_id=db_usuario.tipo_id
        )
        respuesta = Respuesta[schemas.Usuario](
            ok=True, 
            mensaje='Usuario registrado exitósamente. ADVERTENCIA: ESTA ES LA ÚLTIMA VEZ QUE VERÁ SU CONTRASEÑA LIBREMENTE', 
            data=actual
        )
        return respuesta            

# Métodos principalmente para interactuar con la base de datos que por ahora no pondremos en la clase de arriba
def eliminar_usuario(db: Session, cedula: str): 
    usuario = db.query(models.Usuario).filter(models.Usuario.cedula == cedula).first()
    db.delete(usuario)
    db.commit()
    return usuario

def listar_usuarios(db: Session): 
    return db.query(models.Usuario).all()

def listar_artesanos(db: Session): 
    return db.query(models.Usuario).filter(models.Usuario.tipo_id == 1).all()

def listar_clientes(db: Session): 
    return db.query(models.Usuario).filter(models.Usuario.tipo_id == 2).all()

def buscar_usuario(db: Session, cedula: str): 
    retornado = db.query(models.Usuario).filter(models.Usuario.cedula == cedula).first()

    if retornado == None:
        return Respuesta[schemas.Usuario](ok=False, mensaje='Usuario no encontrado')

    usuario = schemas.Usuario(
        cedula=retornado.cedula, 
        nombres=retornado.nombres, 
        apellidos=retornado.apellidos, 
        direccion=retornado.direccion, 
        nacimiento=retornado.nacimiento, 
        correo=retornado.correo, 
        contraseña=retornado.contraseña, 
        tipo_id=retornado.tipo_id
    )
    
    return Respuesta[schemas.Usuario](ok=True, mensaje='Usuario encontrado', data=usuario)

<<<<<<< HEAD
def obtener_usuario(db: Session, cedula: str):
    return db.query(models.Usuario).filter(models.Usuario.cedula == cedula).first()
=======

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
>>>>>>> 63a0bbf7860884724fbd5f7b8f18ce118d65d58a
