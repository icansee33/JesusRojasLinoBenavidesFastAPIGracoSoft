from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    cedula_identidad: str
    nombre: str
    apellido: str
    fecha_nacimiento: date
    direccion: str
    correo_electronico: str
    tipo_usuario: str
    contrasena: str


class UserCreate(UserBase):
   pass

class UserUpdate(UserBase):
    contrasena: str

class User(UserBase):
    id_usuario: int

    class Config:
        orm_mode = True

#producto
class ProductBase(BaseModel):
    id_producto: int
    id_artesano: int
    id_tipo: int
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
    id_resena:int
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


#Tipo
class TipoUserBase(BaseModel):
    nombre: str
    id_tipo: str
 

class TipoCreate(TipoUserBase):
   pass

class  TipoUser(TipoUserBase):
    id_usuario: int

    class Config:
        orm_mode = True