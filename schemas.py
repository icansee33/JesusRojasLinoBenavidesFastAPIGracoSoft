from typing import Optional
<<<<<<< HEAD
from pydantic import BaseModel, EmailStr
=======
from pydantic import BaseModel
>>>>>>> 63a0bbf7860884724fbd5f7b8f18ce118d65d58a
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

<<<<<<< HEAD
class Usuario(UsuarioBase):
    id: int
=======
"""class UserCreate(UserBase):
   pass

class UserUpdate(UserBase):
    contrasena: str

class User(UserBase):
    id_usuario: int
>>>>>>> 63a0bbf7860884724fbd5f7b8f18ce118d65d58a

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

<<<<<<< HEAD
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

=======
"""
>>>>>>> 63a0bbf7860884724fbd5f7b8f18ce118d65d58a
class Token(BaseModel):
    access_token: str
    token_type: str

<<<<<<< HEAD

#producto
=======
class TokenData(BaseModel):
    email: Optional[str] = None
"""
#productoooo
>>>>>>> 63a0bbf7860884724fbd5f7b8f18ce118d65d58a
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

class PedidoBase(BaseModel):
    id_cliente: int
    fecha_pedido: date
    cantidad_productos: int
    metodo_env: str
    estado: str


    class Config:
        orm_mode = True

class PedidoBase(BaseModel):
    id_cliente: int
    fecha_pedido: date
    cantidad_productos: int
    metodo_env: str
    estado: str


class PedidoCreate(PedidoBase):
    pass

class PedidoUpdate(PedidoBase):
    pass

class Pedido(PedidoBase):
    id_pedido: int

    class Config:
        orm_mode = True

class DetallePedidoBase(BaseModel):
    id_pedido: int
    id_producto: int
    cantidad: int
    precio_unitario: float

class DetallePedidoCreate(DetallePedidoBase):
    pass

class DetallePedidoUpdate(DetallePedidoBase):
    pass

class DetallePedido(DetallePedidoBase):
    id_detalle: int


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

<<<<<<< HEAD
class iten for
    
=======

class PedidoProductoBase(BaseModel):
    id_pedido: int
    id_producto: int
    cant_unidades: int
    total: float

class PedidoProductoCreate(PedidoProductoBase):
    pass

class PedidoProductoUpdate(PedidoProductoBase):
    pass

class PedidoProducto(PedidoProductoBase):
    id_pedido_producto: int

    class Config:
        orm_mode = True

>>>>>>> 63a0bbf7860884724fbd5f7b8f18ce118d65d58a
