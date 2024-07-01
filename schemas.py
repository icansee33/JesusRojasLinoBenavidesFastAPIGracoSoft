from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import date

class UsuarioBase(BaseModel):
    cedula: str
    nombres: str
    apellidos: str
    direccion: str
    nacimiento: date
    correo: EmailStr
    tipo_id: int

class UsuarioCrear(UsuarioBase):
    contraseña: str

class Usuario(UsuarioBase):
    id: int

    class Config:
        orm_mode = True

class UsuarioActualizar(BaseModel):
    nombres: Optional[str]
    apellidos: Optional[str]
    direccion: Optional[str]
    nacimiento: Optional[date]
    correo: Optional[EmailStr]
    tipo_id: Optional[int]
    contraseña: Optional[str]

class Respuesta(BaseModel):
    ok: bool
    mensaje: str
    data: Optional[Usuario]

    class Config:
        arbitrary_types_allowed = True

class Token(BaseModel):
    access_token: str
    token_type: str


#producto
class ProductBase(BaseModel):
    id_artesano: int
    id_tipo: str
    nombre: str
    descripcion: str
    categoria: str
    dimensiones: str
    peso: float
    imagen: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id_producto: int

    class Config:
        orm_mode = True

#Reseñas
class ReviewBase(BaseModel):
    id_usuario: int
    id_producto: int
    calificacion: int
    comentario: str

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(ReviewBase):
    pass

class Review(ReviewBase):
    id_review: int

    class Config:
        orm_mode = True

class iten for
    
