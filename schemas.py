from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    nombre: str
    apellido: str
    cedula_identidad: str
    fecha_nacimiento: date
    direccion: str
    correo_electronico: str
    tipo_usuario: str

class UserCreate(UserBase):
    contrasena: str

class User(UserBase):
    id_usuario: int

    class Config:
        orm_mode = True
