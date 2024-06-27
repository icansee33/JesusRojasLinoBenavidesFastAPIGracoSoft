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
    id_artesano: int
    id_tipo: int
    nombre: str
    descripcion: str
    cantidad_disponible: int
    categoria: str
    dimensiones: str
    peso: float
    imagen: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    id_producto: int

class Product(ProductBase):
    
    class Config:
        orm_mode = True

#Reseñas
class ReviewBase(BaseModel):
    id_usuario: int
    id_producto: int
    fecha_invencion: date
    anios_produccion: int
    creador:str
    anecdotas:str


class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(ReviewBase):
    id_resena:int

class Review(ReviewBase):

    class Config:
        orm_mode = True



#Tipo

class TypeProductBase(BaseModel):
    nombre: str

class TypeCreate(TypeProductBase):
    pass

class TypeUpdate(TypeProductBase):
    id_tipo: int

class TypeProduct(TypeProductBase):

    class Config:
        orm_mode = True

