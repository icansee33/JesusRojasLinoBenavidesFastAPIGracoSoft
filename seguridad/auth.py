"""from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dependencias import get_db 
import crudUsuario, models, schemas
from sqlApp.database import SessionLocal
from typing import Union
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Security
from excepcionesUsuario import LoginExpired, Requires_el_Login_de_Exception


class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "27A0D7C4CCCE76E6BE39225B7EEE8BD0EF890DE82D49E459F4C405C583080AB0"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 4

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=self.ALGORITHM)
            return payload
        except jwt.ExpiredSignatureError:
            raise LoginExpired()
        except jwt.JWTError as e:
            raise Requires_el_Login_de_Exception()

    
    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)


    def creacion_para_el_accesso_al_token(self, data: dict, expires_delta: timedelta = None) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes= self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def get_hash_password(self, plain_password):
        return self.pwd_context.hash(plain_password)


    def verify_password(self, plain_password, hash_password):
        return self.pwd_context.verify(plain_password, hash_password)


    async def autenticacion_del_usuario(self, db: Session, cedula: str, contraseña: str):
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
            raise Requires_el_Login_de_Exception()

    def registrar_el_usuario(self, db: Session, usuario: schemas.Usuario_para_Crear):
        db_usuario = models.Usuario(
            cedula=usuario.cedula, 
            nombres=usuario.nombres, 
            apellidos=usuario.apellidos, 
            direccion=usuario.direccion, 
            nacimiento=usuario.nacimiento, 
            correo=usuario.correo, 
            contraseña=self.get_hash_password(usuario.contraseña), 
            tipo_id=usuario.tipo_id)
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
            ok = True, 
            mensaje = 'El Usuario ha sido registrado', 
            data = actual
        )
        return respuesta            


def eliminar_el_usuario(db: Session, cedula: str): 
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
        return Respuesta[schemas.Usuario](ok=False, mensaje='el Usuario no se encontrado')

    usuario = schemas.Usuario(
        cedula=retornado.cedula, 
        nombres=retornado.nombres, 
        apellidos=retornado.apellidos, 
        direccion=retornado.direccion, 
        nacimiento=retornado.nacimiento, 
        correo=retornado.correo, 
        contraseña=retornado.contraseña, 
        tipo_id=retornado.tipo_id) 
    
    return Respuesta[schemas.Usuario](ok=True, mensaje='el Usuario ha sido encontrado', data=usuario)


def obtener_usuario(db: Session, cedula: str):
    return db.query(models.Usuario).filter(models.Usuario.cedula == cedula).first()



"""
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dependencias import get_db 
import crudUsuario, models, schemas
from sqlApp.database import SessionLocal
from typing import Union
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Security
from excepcionesUsuario import LoginExpired, Requires_el_Login_de_Exception


SECRET_KEY = "27A0D7C4CCCE76E6BE39225B7EEE8BD0EF890DE82D49E459F4C405C583080AB0"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verificar_contrasena(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def obtener_hash_contrasena(password):
    return pwd_context.hash(password)



def autenticar_usuario(db: Session, email: str, password: str):
    usuario = crudUsuario.get_user_by_email(db, email)
    if not usuario:
        return False
    if not verificar_contrasena(password, usuario.contrasena):
        return False
    return usuario



def crear_token_acceso(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def buscar_usuario(db: Session, user_id: str):
    user = db.query(models.Usuario).filter(models.Usuario.cedula_identidad == user_id).first()
    if user is None:
        return {"ok": False, "mensaje": "User not found"}
    usuario = schemas.User(
        cedula_identidad = user.cedula_identidad,
        nombre = user.nombre,
        apellido = user.apellido,
        direccion=user.direccion,
        fecha_nacimiento=user.fecha_nacimiento,
        correo_electronico=user.correo_electronico,
        contrasena=user.contrasena,
        tipo_usuario=user.tipo_usuario
    )
    return {"ok": True, "mensaje": "User found", "data": usuario}




#Esto es para el perfil
async def obtener_usuario_actual(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credenciales_exception
    except JWTError:
        raise credenciales_exception
    usuario = crudUsuario.get_user_by_email(db, email)
    if usuario is None:
        raise credenciales_exception
    return usuario



async def obtener_usuario_activo_actual(usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual


    

