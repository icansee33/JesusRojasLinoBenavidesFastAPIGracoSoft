from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Rol, Base
from sqlalchemy import text

# Crea una nueva sesión
Session = sessionmaker()
session = Session()


# Definir la sentencia INSERT
insert_stmt = text("INSERT INTO roles (nombre) VALUES (:nombre)")

# Crear los datos a insertar
roles_data = [
    {'nombre': 'Cliente'},
    {'nombre': 'Artesano'}
]

# Ejecutar la sentencia para cada rol
for rol in roles_data:
    session.execute(insert_stmt, rol)

# Confirmar la transacción
session.commit()

# Cerrar la sesión
session.close()
