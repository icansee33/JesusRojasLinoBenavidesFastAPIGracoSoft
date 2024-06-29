from fastapi import Depends, FastAPI, File, Request, HTTPException, Form, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
import crudUsuario, models, schemas, crudPedido, crudDetallePedido, crudEncargo, auth
import crudProducto, crudResena, crudTipoProducto, schemas
from seguridad.manejarToken import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_user
from sqlApp.database import SessionLocal, engine
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from dependencias import get_db  # Change this import
from typing import Annotated, Optional, Union
import shutil
import os
import uuid
from datetime import date, datetime, timedelta



# Crear todas las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI()

# Montar el directorio estático para servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

#Ya 
# Configurar Jinja2 para la renderización de plantillas
templates = Jinja2Templates(directory="templates")

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


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def read_usuario(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = crudUsuario.get_user_by_ci(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("perfilUsuario.html", {"request": request, "item": item})




# Iniciar sesión
@app.get("/iniciarsesion/", response_class=HTMLResponse)
async def iniciar_sesion_template(request: Request):
    return templates.TemplateResponse("iniciarSesion.html.jinja", {"request": request})

@app.post("/iniciarsesion/", response_class=HTMLResponse)
async def iniciar_sesion_post(
    request: Request,
    correo_electronico: str = Form(...), 
    contrasena: str = Form(...), 
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, correo_electronico, contrasena)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.correo_electronico}, expires_delta=access_token_expires
    )
    return templates.TemplateResponse("baseArtesano.html.jinja", {"request": request, "token": access_token, "user": user})


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
                        id_artesano: int = Form(...), 
                        id_tipo: int = Form(...), 
                        nombre: str = Form(...), 
                        descripcion: str = Form(...),
                        cantidad_disponible: str = Form(...),
                        categoria: str = Form(...), 
                        dimensiones: str = Form(...), 
                        peso: float = Form(...),
                        imagen: UploadFile = File(...),
                        db: Session = Depends(get_db)):
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
                          id_artesano: int = Form(...), 
                          nombre: str = Form(...), 
                          descripcion: str = Form(...), 
                          cantidad_disponible: str = Form(...),
                          categoria: str = Form(...), 
                          dimensiones: str = Form(...), 
                          peso: str = Form(...), 
                          id_tipo: str = Form(...), 
                          imagen: UploadFile = File(...),
                          db: Session = Depends(get_db)):
    imagenpath = save_upload_file(imagen, UPLOAD_DIR)
    print("Imagen path: ", imagenpath)
    product_update = schemas.ProductUpdate(
        id_producto=id_producto, id_artesano=id_artesano,
        nombre=nombre, descripcion=descripcion, cantidad_disponible=cantidad_disponible,categoria=categoria,
        dimensiones=dimensiones, peso=peso, id_tipo=id_tipo, imagen=imagenpath, 
    )
    crudProducto.update_product(db=db, product_id=id_producto, product=product_update)
    products = crudProducto.get_products(db)

    for product in products:
        print("Id:", product.id_producto)
        print("Nombre:", product.nombre)
    return templates.TemplateResponse("listaProducto.html.jinja", {"request": request, "Products": products})






@app.post("/product/delete/{product_id}/", response_class=HTMLResponse)
async def delete_tipo_producto(request: Request, product_id: int, db: Session = Depends(get_db)):
    print("Id producto: ", product_id)  
    crudProducto.delete_product(db=db, product_id=product_id)
    products = crudProducto.get_products(db)
    return templates.TemplateResponse("listaProducto.html.jinja", {"request": request, "Products": products})


@app.get("/product/create/", response_class=HTMLResponse)
async def create_producto_template(request: Request):
    return templates.TemplateResponse("crearProducto.html.jinja", {"request": request})

 

@app.get("/product/update/{product_id}/", response_class=HTMLResponse)
async def update_producto_template(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = crudProducto.get_product_by_id(db, product_id)
    return templates.TemplateResponse("modificarProducto.html.jinja", {"request": request, "product": product})


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


#Resenas
@app.post("/resena/create/", response_model=schemas.ReviewBase)
async def create_resena_post(#current_user: Annotated[schemas.ReviewBase, Depends(get_current_user)],
                        request: Request, 
                        id_producto: str= Form(...),
                        fecha_invencion: str= Form(...),
                        creador: str= Form(...),
                        anios_produccion: str= Form(...), 
                        anecdotas: str= Form(...),
                        db: Session = Depends(get_db)):

    review = schemas.ReviewCreate(
                              id_producto=id_producto,
                              fecha_invencion=fecha_invencion,
                              creador=creador,
                              anios_produccion=anios_produccion,
                              anecdotas=anecdotas
                            )
    crudResena.create_resena(db, review= review)
    reviews = crudResena.get_resenas(db)

    print('Lista resenas:', reviews)
    for review in reviews:
        print("Id:", review.id_resena)
        print("Creador:", review.creador)
    return templates.TemplateResponse("listaResena.html.jinja", {"request": request, "Reviews": reviews})
    

@app.get("/review/create/", response_class=HTMLResponse)
async def create_resena_template(request: Request):
    return templates.TemplateResponse("crearResena.html.jinja", {"request": request})

@app.get("/review/update/{review_id}/", response_class=HTMLResponse)
async def update_resena_template(request: Request, review_id: int, db: Session = Depends(get_db)):
    reviews = crudResena.get_resena_by_id(db, review_id)
    return templates.TemplateResponse("modificarResena.html.jinja", {"request": request, "Reviews": reviews})



@app.get("/review/list", response_class=HTMLResponse, name="read_reviews")
async def read_reviews(request: Request, db: Session = Depends(get_db)):
    reviews = crudResena.get_resenas(db)
    print('Lista reseñas get:', reviews)
    return templates.TemplateResponse("listaResena.html.jinja", {"request": request, "Reviews": reviews})


@app.post("/review/update/", response_class=HTMLResponse)
async def update_resena_post(request: Request, 
                        resena_id: int = Form(...), 
                        id_producto: int = Form(...), 
                        fecha_invencion: str = Form(...), 
                        creador: str = Form(...), 
                        anios_produccion: str = Form(...), 
                        anecdotas: str = Form(...), 
                        db: Session = Depends(get_db)):
    review_update = schemas.ReviewUpdate(
        id_producto=id_producto, fecha_invencion=fecha_invencion, creador=creador,
        anios_produccion=anios_produccion, anecdotas=anecdotas
    )
    crudResena.update_resena(db=db, resena_id=resena_id, resena=review_update)
    reviews = crudResena.get_resenas(db)
    return RedirectResponse("listaResena.html.jinja", {"request": request, "Reviews": reviews})


@app.post("/review/delete/{review_id}/", response_class=HTMLResponse)
async def delete_resena(request: Request, review_id: int, db: Session = Depends(get_db)):
    crudResena.delete_resena(db=db, review_id=review_id)
    reviews = crudResena.get_resenas(db)
    return RedirectResponse("listaResena.html.jinja",{"request": request, "Reviews": reviews})

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
@app.get("/order/list", response_class=HTMLResponse, name="read_pedidos")
async def read_pedidos_artesano(request: Request, db: Session = Depends(get_db)):
    orders = crudPedido.get_orders(db)
    print('Ordenes:', orders)
    return templates.TemplateResponse("listaPedidoArtesano.html.jinja", {"request": request, "Orders": orders})

@app.get("/artisan/orders", response_class=HTMLResponse)
async def get_artisano_orders(request: Request, db: Session = Depends(get_db)):
    orders = crudPedido.get_orders(db)
    return templates.TemplateResponse("listaPedidoArtesano.html.jinja", {"request": request, "Orders": orders})

@app.get("/artisan/order/update/{id_pedido}", response_class=HTMLResponse)
async def update_order_template(request: Request, id_pedido: int, db: Session = Depends(get_db)):
    order = crudPedido.get_order(db, id_pedido)
    return templates.TemplateResponse("updatePedidoArtesano.html.jinja", {"request": request, "Order": order})

@app.post("/artisan/order/update/{id_pedido}", response_model=schemas.Pedido)
async def update_order(
    request: Request,
    id_pedido: int,
    fecha_envio: str = Form(...),
    db: Session = Depends(get_db)
):
    order_update = schemas.PedidoUpdate(fecha_envio=datetime.strptime(fecha_envio, '%Y-%m-%d'))
    updated_order = crudPedido.update_order(db, order_id=id_pedido, order=order_update)
    
    # Crear un registro en la tabla intermedia DetallesPedido (ejemplo)
    detalle_pedido = schemas.DetallePedidoCreate(
        id_pedido=id_pedido,
        cantidad=updated_order.cantidad_productos,
        precio_unitario=10.0  
    )
    crudDetallePedido.create_detalle_pedido(db, detalle_pedido)

    orders = crudPedido.get_orders(db)
    return templates.TemplateResponse("listaPedidoArtesano.html.jinja", {"request": request, "Orders": orders})

@app.get("/order/list", response_class=HTMLResponse, name="read_pedidos")
async def read_productos_pedidos_cliente(request: Request, db: Session = Depends(get_db)):
    orders = crudProducto.get_products(db)
    print('Ordenes:', orders)
    return templates.TemplateResponse("catalagoPedidoCliente.html.jinja", {"request": request, "Orders": orders})


@app.post("/order/create/{id_producto}", response_model=schemas.Pedido)
async def create_order(
    request: Request,
    id_producto: int,
    id_cliente: str = Form(...),
    cantidad_productos: int = Form(...),
    metodo_envio: str = Form(...),
    db: Session = Depends(get_db)
):
    # Obtenemos la fecha actual
    fecha_pedido = datetime.now()

    # Creamos el nuevo pedido
    nuevo_pedido = models.Pedido(
        id_cliente=id_cliente,
        id_producto=id_producto,
        cantidad_productos=cantidad_productos,
        metodo_envio=metodo_envio,
        estado="Solicitado",
        fecha_pedido=fecha_pedido
    )
    
    # Guardamos el nuevo pedido en la base de datos
    crudPedido.create_order(db=db, order=nuevo_pedido)
    
    # Obtenemos la lista de productos para mostrar en la plantilla
    products = crudProducto.get_products(db)

    return templates.TemplateResponse("catalogoPedidoCliente.html.jinja", {"request": request, "Products": products})


@app.get("/order/create/{id_producto}", response_class=HTMLResponse)
async def create_pedido_cliente_template(
    request: Request,
    id_producto: int,
    db: Session = Depends(get_db)
):
    product = crudProducto.get_product_by_id(db, id_producto=id_producto)
    return templates.TemplateResponse("crearPedidoCliente.html.jinja", {"request": request, "product": product})








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
async def perfil_usuario(request: Request, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(auth.obtener_usuario_activo_actual)):
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