from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,Date, Double
from sqlalchemy.orm import relationship
from sqlApp.database import Base


class Usuario(Base):
    __tablename__ = 'usuarios'
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    cedula_identidad = Column(String(20), nullable=False, unique=True)
    fecha_nacimiento = Column(Date, nullable=False)
    direccion = Column(String(255), nullable=False)
    correo_electronico = Column(String(100), nullable=False, unique=True)
    contrasena = Column(String(255), nullable=False)
    tipo_usuario = Column(String(50), nullable=False)

class Producto(Base):
    __tablename__ = 'productos'
    id_producto = Column(Integer, primary_key=True)
    id_artesano = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String, nullable=False)
    categoria = Column(String(50), nullable=False)
    tipo = Column(String(50), nullable=False)
    dimensiones = Column(String(50), nullable=False)
    peso = Column(Double(10, 2), nullable=False)
    imagen = Column(String(255), nullable=False)

    artesano = relationship("Usuario", back_populates="productos")

class Resena(Base):
    __tablename__ = 'resenas'
    id_resena = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    fecha_inversion = Column(Date, nullable=False)
    creador = Column(String(100), nullable=False)
    anios_produccion = Column(Integer, nullable=False)
    anecdotas = Column(String, nullable=True)

    producto = relationship("Producto", back_populates="resenas")

class Pedido(Base):
    __tablename__ = 'pedidos'
    id_pedido = Column(Integer, primary_key=True)
    id_cliente = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_pedido = Column(Date, nullable=False)
    cantidad_productos = Column(Integer, nullable=False)
    metodo_env = Column(String(50), nullable=False)
    estado = Column(String(50), nullable=False)

    cliente = relationship("Usuario", back_populates="pedidos")

class Encargo(Base):
    __tablename__ = 'encargos'
    encargo_id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    cliente_id = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
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

class Invitacion(Base):
    __tablename__ = 'invitaciones'
    id_invitacion = Column(Integer, primary_key=True)
    id_artesano = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    correo_destino = Column(String(100), nullable=False)
    fecha_envio = Column(Date, nullable=False)
    estado = Column(String(50), nullable=False)

    artesano = relationship("Usuario", back_populates="invitaciones")

class Calificacion(Base):
    __tablename__ = 'calificaciones'
    id_calificacion = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    id_cliente = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    calificacion = Column(Integer, nullable=False)
    comentario = Column(String, nullable=True)

    producto = relationship("Producto", back_populates="calificaciones")
    cliente = relationship("Usuario", back_populates="calificaciones")

class Rol(Base):
    __tablename__ = 'roles'
    nombre = Column(String(50), primary_key=True)

class PedidoProducto(Base):
    __tablename__ = 'pedido_producto'
    id_pedido_producto = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey('pedidos.id_pedido'), nullable=False)
    id_producto = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    cant_unidades = Column(Integer, nullable=False)
    total = Column(Double(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="productos")
    producto = relationship("Producto", back_populates="pedidos")