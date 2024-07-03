from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic import BaseModel
from datetime import date
from sqlalchemy import Double


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

class UserCreate(UserBase):
   pass

class UserUpdate(UserBase):
    contrasena: str

class User(UserBase):

    id_usuario: int


    class Config:
        orm_mode = True"""

class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    correo_electronico: str
    direccion: str
    fecha_nacimiento: date
    tipo_usuario: str

class UsuarioCrear(UsuarioBase):
    contrasena: str
    cedula_identidad: int

class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo_electronico: Optional[str] = None
    contrasena: Optional[str] = None
    direccion: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    tipo_usuario: Optional[str] = None

class Usuario(UsuarioBase):

    cedula_identidad: int

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


"""



class Token(BaseModel):
    access_token: str
    token_type: str


#producto

class TokenData(BaseModel):
    email: Optional[str] = None


#productoooo
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
    id_producto: int
    fecha_invencion: date
    creador: str
    anios_produccion: int
    anecdotas: str

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(ReviewBase):
    id_resena: int

class Review(ReviewBase):
    id_resena: int

    class Config:
        orm_mode = True




class PedidoBase(BaseModel):
    id_producto: int
    cedula_identidad: str
    fecha_pedido: date
    cantidad_productos: int
    metodo_envio: str
    precio_unitario: Double
    monto_total: Double
    estado: str

class PedidoCreate(PedidoBase):
    pass

class PedidoUpdate(BaseModel):
    id_producto: int
    id_pedido: int


class Pedido(PedidoBase):
    id_pedido: int

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



#Encargo
class ChargoBase(BaseModel):
    id_producto: int
    cedula_identidad: int
    descripcion_encargo: str
    fecha_encargo: date
    cantidad_productos: int
    metodo_envio: str
    estado_encargo: str

class ChargeCreate(ChargoBase):
    pass

class ChargeUpdate(ChargoBase):
    id_encargo: int

class Pedido(ChargoBase):
    id_encargo: int

    class Config:
        orm_mode = True

##########CALIFICACIONES##########

from pydantic import BaseModel

class CalificacionBase(BaseModel):
    id_producto: int
    id_cliente: int
    calificacion: int
    comentario: str

class CalificacionCreate(CalificacionBase):
    pass

class Calificacion(CalificacionBase):
    id_calificacion: int

    class Config:
        orm_mode = True



class Respuesta(BaseModel):
    ok: bool
    mensaje: str
    data: Optional[User]

    class Config:
        arbitrary_types_allowed = True

