from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Double
from sqlalchemy.orm import relationship
from sqlApp.database import Base

#Hello
class Usuario(Base):
    __tablename__ = 'usuarios'
    cedula_identidad = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    direccion = Column(String(255), nullable=False)
    correo_electronico = Column(String(100), nullable=False, unique=True)
    contrasena = Column(String(255), nullable=False)
    tipo_usuario = Column(String(50), ForeignKey('roles.nombre'), nullable=False)

    rol = relationship("Rol", back_populates="usuarios")
    productos = relationship("Producto", back_populates="artesano")
    pedidos = relationship("Pedido", back_populates="cliente")
    encargos = relationship("Encargo", back_populates="cliente")
    calificaciones = relationship("Calificacion", back_populates="cliente")



class Tipo_Producto(Base):
    __tablename__ = 'tipo_producto'
    id_tipo = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)

    tipos = relationship("Producto", back_populates="tipo")


class Producto(Base):
    __tablename__ = 'productos'
    id_producto = Column(Integer, primary_key=True)
    id_artesano = Column(Integer, ForeignKey('usuarios.cedula_identidad'), nullable=False)
    id_tipo = Column(Integer, ForeignKey('tipo_producto.id_tipo'), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String, nullable=False)
    cantidad_disponible = Column(Integer, nullable=False)
    categoria = Column(String(50), nullable=False)
    dimensiones = Column(String(50), nullable=False)
    peso = Column(Double(10, 2), nullable=False)
    imagen = Column(String(255), nullable=False)

    tipo = relationship("Tipo_Producto", back_populates="tipos")
    artesano = relationship("Usuario", back_populates="productos")
    resenas = relationship("Resena", back_populates="producto")
    encargos = relationship("Encargo", back_populates="producto")
    detalles = relationship("DetallePedido", back_populates="producto")
    calificaciones = relationship("Calificacion", back_populates="producto")
    pedidos = relationship("PedidoProducto", back_populates="producto")



class Resena(Base):
    __tablename__ = 'resenas'
    id_resena = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    fecha_invencion = Column(Date, nullable=False)
    creador = Column(String(100), nullable=False)
    anios_produccion = Column(Integer, nullable=False)
    anecdotas = Column(String, nullable=True)

    producto = relationship("Producto", back_populates="resenas")

class Pedido(Base):
    __tablename__ = 'pedidos'
    id_pedido = Column(Integer, primary_key=True)
    id_cliente = Column(Integer, ForeignKey('usuarios.cedula_identidad'), nullable=False)
    fecha_pedido = Column(Date, nullable=False)
    cantidad_productos = Column(Integer, nullable=False)
    metodo_env = Column(String(50), nullable=False)
    estado = Column(String(50), nullable=False)

    cliente = relationship("Usuario", back_populates="pedidos")
    detalles = relationship("DetallePedido", back_populates="pedido")
    productos = relationship("PedidoProducto", back_populates="pedido")

class Encargo(Base):
    __tablename__ = 'encargos'
    id_encargo = Column(Integer, primary_key=True)
    id_producto= Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    cedula_identidad = Column(Integer, ForeignKey('usuarios.cedula_identidad'), nullable=False)
    estado_encargo = Column(String(50), nullable=False)
    fecha_encargo = Column(Date, nullable=False)
    metodo_envio = Column(String(50), nullable=False)
    descripcion_encargo = Column(String, nullable=False)

    producto = relationship("Producto", back_populates="encargos")
    cliente = relationship("Usuario", back_populates="encargos")

class DetallePedido(Base):
    __tablename__ = 'detalles_pedido'
    id_detalle = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey('pedidos.id_pedido'), nullable=False)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Double(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles")

class Calificacion(Base):
    __tablename__ = 'calificaciones'
    id_calificacion = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    id_cliente = Column(Integer, ForeignKey('usuarios.cedula_identidad'), nullable=False)
    calificacion = Column(Integer, nullable=False)
    comentario = Column(String, nullable=True)

    producto = relationship("Producto", back_populates="calificaciones")
    cliente = relationship("Usuario", back_populates="calificaciones")

class Rol(Base):
    __tablename__ = 'roles'
    nombre = Column(String(50), primary_key=True)

    usuarios = relationship("Usuario", back_populates="rol")

class PedidoProducto(Base):
    __tablename__ = 'pedido_producto'
    id_pedido_producto = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey('pedidos.id_pedido'), nullable=False)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    cant_unidades = Column(Integer, nullable=False)
    total = Column(Double(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="productos")
    producto = relationship("Producto", back_populates="pedidos")