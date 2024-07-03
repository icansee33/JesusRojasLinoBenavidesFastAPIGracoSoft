from fastapi import Depends, FastAPI, File, Request, HTTPException, Form, Response, UploadFile, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware import Middleware
from sqlalchemy import Double
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import crudUsuario, models, schemas, crudPedido, crudDetallePedido, crudEncargo, seguridad.auth as auth
import crudProducto, crudResena, crudTipoProducto, schemas
from seguridad.auth import ACCESS_TOKEN_EXPIRE_MINUTES, autenticar_usuario, crear_token_acceso, obtener_usuario_activo_actual
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from dependencias import get_db  # Change this import
from typing import Annotated, Optional, Union
import shutil
import os
import uuid
from datetime import date, datetime, timedelta
from sqlApp.database import SessionLocal, engine


# Crear todas las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI con el middleware de sesión
app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key="your_secret_key")
])

# Montar el directorio estático para servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurar Jinja2 para la renderización de plantillas
templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="iniciar_sesion_post")

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/usuario/create/", response_model=schemas.UserBase)
async def create_usuario_post(request: Request, 
                        cedula_identidad: str = Form(...), 
                        nombre: str = Form(...), 
                        apellido: str = Form(...), 
                        fecha_nacimiento: str = Form(...), 
                        direccion: str = Form(...), 
                        correo_electronico: str = Form(...), 
                        contrasena: str = Form(...), 
                        tipo_usuario : str = Form(...),
                        db: Session = Depends(get_db)):
    print("Usuario: ", correo_electronico)
    user = schemas.UserCreate(cedula_identidad=cedula_identidad, 
                              nombre=nombre, 
                              apellido=apellido, 
                              fecha_nacimiento=fecha_nacimiento, 
                              direccion=direccion,
                              correo_electronico=correo_electronico, 
                              contrasena=contrasena, 
                              tipo_usuario=tipo_usuario)
    db_user = crudUsuario.get_user_by_email(db, email=user.correo_electronico)
    print("Db user: ", db_user)
    if db_user: 
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crudUsuario.get_user_by_ci(db, user_id=user.cedula_identidad)
    if db_user: 
        raise HTTPException(status_code=400, detail="CI already registered")
    crudUsuario.create_user(db=db, user=user)
    return templates.TemplateResponse("crearUsuario.html.jinja", {"request": request})


@app.get("/usuario/create/", response_class=HTMLResponse)
async def create_usuario_template(request: Request):
    print("Usuario get: ", )
    return templates.TemplateResponse("crearUsuario.html.jinja", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def home_no_iniciado(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("homeNoIniciado.html.jinja", {"request": request})

@app.get("/base/artesano/", response_class=HTMLResponse)
async def base_artesano_iniciado(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("baseArtesano.html.jinja", {"request": request})

@app.get("/base/cliente/", response_class=HTMLResponse)
async def base_cliente_iniciado(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("baseCliente.html.jinja", {"request": request})


"""
@app.get('/home/artesano', response_class=HTMLResponse)
def home_artesano(request: Request):
    user_type = request.session.get('user_type')
    if user_type == 1:
        return templates.TemplateResponse("HArtesano.html", {"request": request})
    return RedirectResponse(url='/usuarios/iniciarsesion.html', status_code=status.HTTP_303_SEE_OTHER)

@app.get('/home/cliente', response_class=HTMLResponse)
def home_cliente(request: Request):
    user_type = request.session.get('user_type')
    if user_type == 2:
        return templates.TemplateResponse("HCliente.html", {"request": request})
    return RedirectResponse(url='/usuarios/iniciarsesion.html', status_code=status.HTTP_303_SEE_OTHER)

"""



async def read_usuario(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = crudUsuario.get_user_by_ci(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("perfilUsuario.html", {"request": request, "item": user})


# Iniciar sesión
@app.get("/iniciarsesion/", response_class=HTMLResponse)
async def iniciar_sesion_template(request: Request):
    return templates.TemplateResponse("iniciarSesion.html.jinja", {"request": request})


@app.post('/iniciar_sesion', response_class=HTMLResponse)
async def iniciar_sesion_post(request: Request,
                   correo_electronico: str = Form(...),               
                   contrasena: str = Form(...), 
                   db: Session = Depends(get_db)):
    user = autenticar_usuario(db, correo_electronico, contrasena)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Error, Incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"}
        )
    tiempo_expiracion = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    nombre= f'{user.nombre} {user.apellido}'
    token_acceso = auth.crear_token_acceso(
        data={'cedula_identidad': user.cedula_identidad,
              'nombre': nombre,
              'tipo_usuario': user.tipo_usuario},
        expires_delta=tiempo_expiracion
    )
    request.session['cedula_identidad'] = user.cedula_identidad
    request.session['tipo_usuario'] = user.tipo_usuario
    
    if user.tipo_usuario == "Cliente":
        return RedirectResponse(url="/base/cliente/", status_code=status.HTTP_303_SEE_OTHER)
    elif user.tipo_usuario == "Artesano":
        return RedirectResponse(url="/base/artesano/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        print("user", user.tipo_usuario )
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.middleware("http")
async def create_auth_header(request: Request, call_next):
    if ("Authorization" not in request.headers 
        and "Authorization" in request.cookies):
        access_token = request.cookies["Authorization"]
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer {access_token}".encode(),
            )
        )
    elif ("Authorization" not in request.headers 
        and "Authorization" not in request.cookies): 
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer 12345".encode(),
            )
        )
        
    response = await call_next(request)
    return response




#Producto

#Codigo de imagen de producto

UPLOAD_DIR = "static/images/"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)




def save_upload_file(upload_file: UploadFile, upload_dir: str):
    filename, file_extension = os.path.splitext(upload_file.filename)
    unique_filename = f"{filename}_{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path

@app.post("/product/create/", response_model=schemas.ProductBase)
async def create_producto_post(
                        request: Request, 
                        id_tipo: int = Form(...), 
                        nombre: str = Form(...), 
                        descripcion: str = Form(...),
                        cantidad_disponible: str = Form(...),
                        categoria: str = Form(...), 
                        dimensiones: str = Form(...), 
                        peso: float = Form(...),
                        imagen: UploadFile = File(...),
                        db: Session = Depends(get_db)):
    id_artesano = request.session.get('cedula_identidad')
    if not id_artesano:
        raise HTTPException(status_code=401, detail="Unauthorized. Please log in as an artesano.")
    
    imagenpath = save_upload_file(imagen, UPLOAD_DIR)
    print("Imagen path: ", imagenpath)
    product = schemas.ProductCreate(
                              id_artesano=int(id_artesano),
                              id_tipo=int(id_tipo),
                              nombre=nombre,
                              descripcion=descripcion,
                              cantidad_disponible=cantidad_disponible,
                              categoria=categoria, 
                              dimensiones=dimensiones,
                              imagen=imagenpath, 
                              peso=peso)
    crudProducto.create_product(db=db, product=product)
    products = crudProducto.get_products(db)
    for product in products:
        print("Id:", product.id_tipo)
        print("Nombre:", product.nombre)
    return templates.TemplateResponse("listaProducto.html.jinja", {"request": request, "Products": products})

@app.post("/product/update/", response_class=HTMLResponse)
async def update_producto_post(request: Request, 
                          id_producto: int = Form(...),
                          nombre: str = Form(...), 
                          descripcion: str = Form(...), 
                          cantidad_disponible: str = Form(...),
                          categoria: str = Form(...), 
                          dimensiones: str = Form(...), 
                          peso: str = Form(...), 
                          id_tipo: str = Form(...), 
                          imagen: UploadFile = File(...),
                          db: Session = Depends(get_db)):
    id_artesano = request.session.get('cedula_identidad')
    if not id_artesano:
        raise HTTPException(status_code=401, detail="Unauthorized. Please log in as an artesano.")
    

    imagenpath = save_upload_file(imagen, UPLOAD_DIR)
    print("Imagen path: ", imagenpath)

    product_update = schemas.ProductUpdate(
        id_producto=id_producto, id_artesano=int(id_artesano),
        nombre=nombre, descripcion=descripcion, cantidad_disponible=cantidad_disponible,categoria=categoria,
        dimensiones=dimensiones, peso=peso, id_tipo=id_tipo, imagenpath=imagenpath, 
    )
    crudProducto.update_product(db=db, product_id=id_producto, product=product_update)
    products = crudProducto.get_products(db)

    for product in products:
        print("Id:", product.id_producto)
        print("Nombre:", product.nombre)
    return templates.TemplateResponse("listaProducto.html.jinja", {"request": request, "Products": products})



@app.get("/product/create/", response_class=HTMLResponse)
async def create_producto_template(request: Request, db: Session = Depends(get_db)):
    types = crudTipoProducto.get_types(db) 
    return templates.TemplateResponse("crearProducto.html.jinja", {"request": request, "types": types})


@app.get("/product/update/{product_id}/", response_class=HTMLResponse)
async def update_producto_template(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = crudProducto.get_product_by_id(db, product_id)
    types = crudTipoProducto.get_types(db) 
    return templates.TemplateResponse("modificarProducto.html.jinja", {"request": request, "product": product, "types": types})


@app.get("/product/list/", response_class=HTMLResponse, name="read_productos")
async def read_productos(request: Request, db: Session = Depends(get_db)):
    print("Fetching product list")
    products = crudProducto.get_products(db)
    if not products:
        print("No products found")
    else:
        print(f"Found {len(products)} products")
        for product in products:
            print("Product ID:", product.id_producto)
            print("Product Name:", product.nombre)
    return templates.TemplateResponse("listaProducto.html.jinja", {"request": request, "Products": products})



@app.post("/product/delete/{product_id}/", response_class=HTMLResponse)
async def delete_producto(request: Request, product_id: int, db: Session = Depends(get_db)):
    crudProducto.delete_product(db=db, product_id=product_id)
    return RedirectResponse(url='/product/list/', status_code=303)




#Resenas
# Debugging to check the type and content of reviews
@app.post("/resena/create/", response_model=schemas.ReviewBase)
async def create_resena_post(request: Request, 
                             id_producto: str= Form(...),
                             fecha_invencion: str= Form(...),
                             creador: str= Form(...),
                             anios_produccion: str= Form(...), 
                             anecdotas: str= Form(...),
                             db: Session = Depends(get_db)):
    # Convert fecha_invencion to date
    fecha_invencion_date = datetime.strptime(fecha_invencion, '%Y-%m-%d').date()

    review = schemas.ReviewCreate(
        id_producto=id_producto,
        fecha_invencion=fecha_invencion_date,
        creador=creador,
        anios_produccion=anios_produccion,
        anecdotas=anecdotas
    )
    crudResena.create_resena(db, review=review)
    reviews = crudResena.get_resenas(db)

    # Print type and content of reviews
    print('Type of reviews:', type(reviews))
    print('Content of reviews:', reviews)

    for review in reviews:
        print("Type of review:", type(review))
        print("Id:", review.id_resena)
        print("Creador:", review.creador)

    return templates.TemplateResponse("listaResena.html.jinja", {"request": request, "Reviews": reviews})


@app.get("/review/create/", response_class=HTMLResponse)
async def create_resena_template(request: Request):
    return templates.TemplateResponse("crearResena.html.jinja", {"request": request})


@app.post("/review/delete/{review_id}/", response_class=HTMLResponse)
async def delete_review(request: Request, review_id: int, db: Session = Depends(get_db)):
    print("Id reseña: ", review_id)  
    crudResena.delete_resena(db=db, review_id=review_id)
    reviews = crudResena.get_resenas(db)
    return templates.TemplateResponse("listaResena.html.jinja", {"request": request, "Reviews": reviews})


@app.get("/review/list/", response_class=HTMLResponse, name="read_reviews")
async def read_reviews(request: Request, db: Session = Depends(get_db)):
    reviews = crudResena.get_resenas(db)
    print('Lista reseñas get:', reviews)
    return templates.TemplateResponse("listaResena.html.jinja", {"request": request, "Reviews": reviews})





#Tipo Producto
@app.post("/type_product/create/", response_model=schemas.TypeProductBase)
async def create_tipo_producto_post(
    request: Request, 
    nombre: str = Form(...), 
    db: Session = Depends(get_db),
    #current_user: models.Usuario = Depends(get_current_user) 
):
    print("Tipo Product: ", nombre)
    type_product = schemas.TypeCreate(nombre=nombre)
    crudTipoProducto.create_type_product(db=db, type_product=type_product)
    types = crudTipoProducto.get_types(db)

    print('Lista tipos:', types)
    for type in types:
        print("Id:", type.id_tipo)
        print("Nombre:", type.nombre)
    return templates.TemplateResponse("listaTipoProducto.html.jinja", {"request": request, "typesProducts": types})


@app.get("/type_product/list", response_class=HTMLResponse, name="read_tipos")
async def read_tipos(request: Request, db: Session = Depends(get_db)):
    types = crudTipoProducto.get_types(db)
    print('Lista tipos get:', types)
    return templates.TemplateResponse("listaTipoProducto.html.jinja", {"request": request, "typesProducts": types})


@app.get("/type_product/update/{type_id}/", response_class=HTMLResponse)
async def update_tipo_producto_template(request: Request, type_id: int, db: Session = Depends(get_db)):
    type_product = crudTipoProducto.get_type_by_id(db, type_id)
    return templates.TemplateResponse("modificarTipoProducto.html.jinja", {"request": request, "type_product": type_product})



@app.post("/type_product/delete/{type_id}/", response_class=HTMLResponse)
async def delete_tipo_producto(request: Request, type_id: int, db: Session = Depends(get_db)):
    print("Id producto: ", type_id)  
    crudTipoProducto.delete_type_product(db=db, type_id=type_id)
    types = crudTipoProducto.get_types(db)
    return templates.TemplateResponse("listaTipoProducto.html.jinja", {"request": request, "typesProducts": types})


@app.post("/type_product/update/", response_class=HTMLResponse)
async def update_tipo_producto_post(
    request: Request, 
    id_tipo: int = Form(...),  
    nombre: str = Form(...), 
    db: Session = Depends(get_db)
):
    type_update = schemas.TypeUpdate(id_tipo=id_tipo, nombre=nombre)
    crudTipoProducto.update_type_product(db=db, type_id=id_tipo, type=type_update)
    types = crudTipoProducto.get_types(db)
    return templates.TemplateResponse("listaTipoProducto.html.jinja", {"request": request, "typesProducts": types})


@app.get("/type_product/create/", response_class=HTMLResponse)
async def create_tipo_producto_template(request: Request):
    return templates.TemplateResponse("crearTipoProducto.html.jinja", {"request": request})

#Pedido


# Ruta para redirigir al cliente al catálogo de productos
@app.get("/order/client/list/", response_class=HTMLResponse, name="read_productos_pedidos_cliente")
async def read_productos_pedidos_cliente(request: Request, db: Session = Depends(get_db)):
    products = crudProducto.get_products(db)
    return templates.TemplateResponse("catalogoPedidoCliente.html.jinja", {"request": request, "products": products})

# Ruta para redirigir al cliente a la interfaz de solicitar pedido, cuando se abra la interfaz debe saber el id del producto
@app.get("/order/client/request/{id_producto}", response_class=HTMLResponse)
async def request_pedido_cliente(request: Request, id_producto: int, db: Session = Depends(get_db)):
    product = crudProducto.get_product_by_id(db, id_producto)
    return templates.TemplateResponse("crearPedidoCliente.html.jinja", {"request": request, "product": product})

# Ruta para redirigir al artesano a la interfaz de establecer pedido
@app.get("/order/artesan/update/{order_id}", response_class=HTMLResponse)
async def set_up_pedido_artesano_template(request: Request, order_id: int, db: Session = Depends(get_db)):
    order = crudPedido.get_order_by_id(db, order_id)
    return templates.TemplateResponse("modificarPedidoArtesano.html.jinja", {"request": request, "order": order})

# Ruta para redirigir al cliente a la lista de sus pedidos
@app.get("/order/client/orders/", response_class=HTMLResponse, name="read_pedidos_cliente")
async def read_pedidos_cliente(request: Request, db: Session = Depends(get_db)):
    orders = crudPedido.get_orders(db)
    return templates.TemplateResponse("listaPedidoCliente.html.jinja", {"request": request, "orders": orders})

# Ruta para redirigir al artesano al catálogo de pedidos (le aparecen los pedidos de todos los clientes)
@app.get("/order/product/artesan/list/", response_class=HTMLResponse, name="read_pedidos_artesano")
async def read_pedidos_artesano(request: Request, db: Session = Depends(get_db)):
    orders = crudPedido.get_orders(db)
    return templates.TemplateResponse("listaPedidoArtesano.html.jinja", {"request": request, "orders": orders})

# Ruta para que el cliente cree un pedido
@app.post("/order/create/{id_producto}", response_model=schemas.Pedido)
async def solicitar_pedido(
    request: Request,
    id_producto: int = Form(...),
    cedula_identidad: str = Form(...),
    cantidad_productos: int = Form(...),
    metodo_envio: str = Form(...),
    precio_unitario: float = Form(...), 
    db: Session = Depends(get_db)
):
    # Validar disponibilidad del producto
    product = crudProducto.get_product_by_id(db, id_producto)
    if not product or product.cantidad_disponible < cantidad_productos:
        return templates.TemplateResponse("error.html.jinja", {"request": request, "message": "Cantidad de productos no disponible."})
    
    # Calcular el monto total y el IVA
    monto_base = cantidad_productos * precio_unitario
    iva = monto_base * 0.16
    monto_total = monto_base + iva

    fecha_pedido = date.today()
    estado = "Solicitado"

    order = schemas.PedidoCreate(
        id_producto=id_producto,
        cedula_identidad=cedula_identidad,
        cantidad_productos=cantidad_productos,
        metodo_envio=metodo_envio,
        fecha_pedido=fecha_pedido,
        precio_unitario=precio_unitario,
        monto_total=monto_total,
        estado=estado
    )
    
    crudPedido.create_order(db, order)
    orders = crudPedido.get_orders(db)
    return templates.TemplateResponse("catalogoPedidoCliente.html.jinja", {"request": request, "products": orders})

# Ruta para que el artesano establezca un pedido
@app.post("/order/artesan/set_up", response_class=HTMLResponse)
async def update_tipo_producto_post(
    request: Request,
    id_pedido: int = Form(...),
    id_producto: int = Form(...),
    cedula_identidad: str = Form(...),
    cantidad_productos: int = Form(...),
    metodo_envio: str = Form(...),
    precio_unitario: float = Form(...),
    monto_total: float = Form(...),
    db: Session = Depends(get_db)
):
    fecha_pedido = date.today()
    estado = "Procesando"

    order_update = schemas.PedidoUpdate(
        id_producto=id_producto,
        cedula_identidad=cedula_identidad,
        cantidad_productos=cantidad_productos,
        metodo_envio=metodo_envio,
        fecha_pedido=fecha_pedido,
        precio_unitario=precio_unitario,
        monto_total=monto_total,
        estado=estado
    )
    
    crudPedido.update_order(db, order_id=id_pedido, order=order_update)
    orders = crudPedido.get_orders(db)
    return templates.TemplateResponse("listaPedidoArtesano.html.jinja", {"request": request, "Orders": orders})

# Ruta para que el cliente acepte un pedido
@app.post("/order/client/accept", response_class=HTMLResponse)
async def accept_pedido_cliente(
    request: Request,
    id_pedido: int = Form(...),
    db: Session = Depends(get_db)
):
    order = crudPedido.get_order_by_id(db, order_id=id_pedido)
    if order:
        order.estado = "Aceptado"
        product = crudProducto.get_product_by_id(db, order.id_producto)
        product.cantidad_disponible -= order.cantidad_productos
        db.commit()

    orders = crudPedido.get_orders(db)
    return templates.TemplateResponse("listaPedidoCliente.html.jinja", {"request": request, "orders": orders})






@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = auth.autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.crear_token_acceso(
        data={"sub": usuario.correo_electronico}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/perfil_usuario/", response_class=HTMLResponse)
async def perfil_usuario(request: Request, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_activo_actual)):
    return templates.TemplateResponse("perfil.html.jinja", {"request": request, "usuario": usuario_actual})

@app.post("/perfil_usuario/update/")
async def update_perfil_usuario(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo_electronico: str = Form(...),
    direccion: str = Form(...),
    contrasena: str = Form(...),
    cedula_identidad: str = Form(...),
    tipo_usuario: str = Form(...),
    fecha_nacimiento: date = Form(...),

    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(auth.obtener_usuario_activo_actual)
):
    usuario_actualizado = schemas.UserUpdate(
        nombre=nombre,
        apellido=apellido,
        correo_electronico=correo_electronico,
        fecha_nacimiento=fecha_nacimiento,
        direccion=direccion,
        contrasena=contrasena,
        cedula_identidad=cedula_identidad,
        tipo_usuario= tipo_usuario
    )
    usuario = crudUsuario.update_user(db=db, 
                                      user_id=usuario_actual.cedula_identidad, 
                                      usuario_actualizado=usuario_actualizado, 
                                      fecha_nacimiento=fecha_nacimiento, 
                                      direccion= direccion, 
                                      contrasena= contrasena,
                                      cedula_identidad= cedula_identidad,
                                      tipo_usuario= tipo_usuario,
                                      )
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return templates.TemplateResponse("perfil.html.jinja", {"request": request})

"""


#Encargo
@app.post("/charge/create", response_class=HTMLResponse)
async def create_charge_post(request: Request, 
                             id_producto: int = Form(...),
                             cedula_identidad: int = Form(...),
                             descripcion_encargo: str = Form(...),
                             fecha_encargo: date = Form(...),
                             metodo_envio: str = Form(...),
                             estado_encargo: str = Form(...),
                             db: Session = Depends(get_db)):
    charge = schemas.ChargeCreate(
        id_producto=id_producto,
        cedula_identidad=cedula_identidad,
        descripcion_encargo=descripcion_encargo,
        fecha_encargo=fecha_encargo,
        metodo_envio=metodo_envio,
        estado_encargo=estado_encargo
    )
    crudEncargo.create_charge(db=db, charge=charge)
    charges = crudEncargo.get_charge(db)
    return templates.TemplateResponse("listaEncargoArtesano.html.jinja", {"request": request, "Orders": charges})


@app.get("/charge/list", response_class=HTMLResponse)
async def read_charges(request: Request, db: Session = Depends(get_db)):
    charges = crudEncargo.get_charge(db=db)
    return templates.TemplateResponse("listaEncargoArtesano.html.jinja", {"request": request, "Orders": charges})

@app.get("/charge/update/{charge_id}", response_class=HTMLResponse)
async def update_charge_template(charge_id: int, request: Request, db: Session = Depends(get_db)):
    charge = crudEncargo.get_charge_by_id(db=db, charge_id=charge_id)
    return templates.TemplateResponse("modificarEncargoArtesano.html.jinja", {"request": request, "charge": charge})

@app.post("/charge/update/{charge_id}", response_class=HTMLResponse)
async def update_charge_post(
                            request: Request,
                            charge_id:  str = Form(...),
                            descripcion_encargo: str = Form(...),
                            metodo_envio: str = Form(...),
                            estado_encargo: str = Form(...), 
                            db: Session = Depends(get_db)):
    charge_update = schemas.ChargeUpdate(
        id_encargo=charge_id,
        descripcion_encargo=descripcion_encargo,
        metodo_envio=metodo_envio,
        estado_encargo=estado_encargo
    )
    crudEncargo.update_charge(db=db, charge_id=charge_id, charge=charge_update)
    charges = crudEncargo.get_charge(db)
    return templates.TemplateResponse("listaEncargoArtesano.html.jinja", {"request": request, "Orders": charges})

@app.post("/charge/delete/{charge_id}", response_class=HTMLResponse)
async def delete_charge(charge_id: int, request: Request, db: Session = Depends(get_db)):
    crudEncargo.delete_charge(db=db, charge_id=charge_id)
    charges = crudEncargo.get_charge(db)
    return templates.TemplateResponse("listaEncargoArtesano.html.jinja", {"request": request, "Orders": charges})

@app.get("/charge/create", response_class=HTMLResponse)
async def create_charge_template(request: Request):
    return templates.TemplateResponse("crearEncargoArtesano.html.jinja", {"request": request})"""