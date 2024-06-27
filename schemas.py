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

