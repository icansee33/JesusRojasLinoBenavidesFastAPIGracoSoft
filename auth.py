from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dependencias import get_db  # Change this import
import crudUsuario, models, schemas
from sqlApp.database import SessionLocal

SECRET_KEY = "your_secret_key"  # Cambia esto por una clave secreta más segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verificar_contrasena(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def obtener_hash_contrasena(password):
    return pwd_context.hash(password)

def autenticar_usuario(db: Session, email: str, password: str):
    usuario = crudUsuario.obtener_usuario_por_email(db, email)
    if not usuario:
        return False
    if not verificar_contrasena(password, usuario.contrasena):
        return False
    return usuario

def crear_token_acceso(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
    usuario = crudUsuario.obtener_usuario_por_email(db, email)
    if usuario is None:
        raise credenciales_exception
    return usuario

async def obtener_usuario_activo_actual(usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual