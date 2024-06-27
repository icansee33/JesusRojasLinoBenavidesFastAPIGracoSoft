from fastapi import Depends, FastAPI, File, Request, HTTPException, Form, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import crudUsuario, models, schemas, crudProducto,  crudpedidos
from seguridad.manejarToken import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token
from sqlApp.database import SessionLocal, engine
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER
from fastapi import Depends
import shutil
import os
import uuid

auth_handler = AuthHandler()

from crudUsuario import AuthHandler

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
    print("Hasta acá va bien")
    crudUsuario.create_user(db=db, user=user)
    return templates.TemplateResponse("homeNoIniciado.html.jinja", {"request": request})


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


@app.get("/usuario/update/{user_id}/", response_class=HTMLResponse)
async def update_usuario_form(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = crudUsuario.get_user_by_ci(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("modificarUsuario.html.jinja", {"request": request, "item": item})

@app.post("/usuario/update/{user_id}/", response_class=HTMLResponse)
async def update_item(request: Request, item_id: int, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    usuario_update = schemas.UserUpdate(name=name, description=description)
    crudUsuario.update_user(db=db, item_id=item_id, item=usuario_update)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

@app.post("/usuario/delete/{user_id}", response_class=HTMLResponse)
async def delete_usuario(request: Request, item_id: int, db: Session = Depends(get_db)):
    crudUsuario.delete_user(db=db, item_id=item_id)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

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
    
    #hola mundo 
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
    return templates.TemplateResponse("crearUsuario.html.jinja", {"request": request, "token": access_token, "user": user})

#Codigo de imagen de producto

UPLOAD_DIR = "static/images/"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_upload_file(upload_file: UploadFile, upload_dir: str):
    filename, file_extension = os.path.splitext(upload_file.filename)
    unique_filename = f"{filename}_{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path

@app.post("/item/create/", response_class=HTMLResponse)
async def create_item(
    request: Request,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    categoria: str = Form(...),
    tipo: str = Form(...),
    dimensiones: str = Form(...),
    peso: float = Form(...),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    artesano_id = 1 
    image_path = save_upload_file(imagen, UPLOAD_DIR)

    item = schemas.ProductCreate(
        nombre=nombre,
        descripcion=descripcion,
        categoria=categoria,
        tipo=tipo,
        dimensiones=dimensiones,
        peso=peso,
        imagen=image_path 
    )
    crudProducto.create_product(db=db, item=item, artesano_id=artesano_id)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

@app.get("/pedidos/", response_class=HTMLResponse)
async def read_pedidos(request: Request, db: Session = Depends(get_db)):
    pedidos = crudpedidos.get_pedidos(db)
    return templates.TemplateResponse("pedido_list.html", {"request": request, "pedidos": pedidos})

@app.get("/pedido/create/", response_class=HTMLResponse)
async def create_pedido_form(request: Request):
    return templates.TemplateResponse("pedido_create.html", {"request": request})

@app.post("/pedido/create/", response_class=HTMLResponse)
async def create_pedido(
    request: Request,
    id_cliente: int = Form(...),
    fecha_pedido: date = Form(...),
    cantidad_productos: int = Form(...),
    metodo_env: str = Form(...),
    estado: str = Form(...),
    db: Session = Depends(get_db)
):
    pedido = schemas.PedidoCreate(
        id_cliente=id_cliente,
        fecha_pedido=fecha_pedido,
        cantidad_productos=cantidad_productos,
        metodo_env=metodo_env,
        estado=estado
    )
    crudpedidos.create_pedido(db=db, pedido=pedido)
    return RedirectResponse("/pedidos/", status_code=HTTP_303_SEE_OTHER)

@app.get("/pedido/{pedido_id}/", response_class=HTMLResponse)
async def read_pedido(request: Request, pedido_id: int, db: Session = Depends(get_db)):
    pedido = crudpedidos.get_pedido(db, pedido_id=pedido_id)
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido not found")
    return templates.TemplateResponse("pedido_detail.html", {"request": request, "pedido": pedido})

@app.get("/pedido/edit/{pedido_id}/", response_class=HTMLResponse)
async def edit_pedido_form(request: Request, pedido_id: int, db: Session = Depends(get_db)):
    pedido = crudpedidos.get_pedido(db, pedido_id=pedido_id)
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido not found")
    return templates.TemplateResponse("pedido_edit.html", {"request": request, "pedido": pedido})

@app.post("/pedido/edit/{pedido_id}/", response_class=HTMLResponse)
async def edit_pedido(
    request: Request,
    pedido_id: int,
    id_cliente: int = Form(...),
    fecha_pedido: date = Form(...),
    cantidad_productos: int = Form(...),
    metodo_env: str = Form(...),
    estado: str = Form(...),
    db: Session = Depends(get_db)
):
    pedido_update = schemas.PedidoUpdate(
        id_cliente=id_cliente,
        fecha_pedido=fecha_pedido,
        cantidad_productos=cantidad_productos,
        metodo_env=metodo_env,
        estado=estado
    )
    updated_pedido = crudpedidos.update_pedido(db=db, pedido_id=pedido_id, pedido=pedido_update)
    if updated_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido not found")
    return RedirectResponse("/pedidos/", status_code=HTTP_303_SEE_OTHER)

@app.post("/pedido/delete/{pedido_id}/", response_class=HTMLResponse)
async def delete_pedido(request: Request, pedido_id: int, db: Session = Depends(get_db)):
    deleted_pedido = crudpedidos.delete_pedido(db=db, pedido_id=pedido_id)
    if deleted_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido not found")
    return RedirectResponse("/pedidos/", status_code=HTTP_303_SEE_OTHER)
    

