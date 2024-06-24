from fastapi import Depends, FastAPI, File, Request, HTTPException, Form, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import crudUsuario, crudProducto, crudResena, crudTipoProducto, models, schemas
from seguridad.manejarToken import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_user
import crudUsuario, models, schemas, crudProducto
from sqlApp.database import SessionLocal, engine
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from fastapi import Depends
from typing import Annotated, Union
import shutil
import os
import uuid
from datetime import datetime, timedelta

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
    return RedirectResponse("/", status_code=HTTP_400_BAD_REQUEST)

@app.post("/usuario/delete/{user_id}", response_class=HTMLResponse)
async def delete_usuario(request: Request, item_id: int, db: Session = Depends(get_db)):
    crudUsuario.delete_user(db=db, item_id=item_id)
    return RedirectResponse("/", status_code=HTTP_400_BAD_REQUEST)




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
    return templates.TemplateResponse("baseArtesano.html.jinja", {"request": request, "token": access_token, "user": user})
  

#Producto
@app.post("/producto/create/", response_model=schemas.ProductBase,)
async def create_product_post(#current_user: Annotated[schemas.UserBase, Depends(get_current_user) ],
                        request: Request, 
                        id_producto: str = Form(...), 
                        id_artesano: str = Form(...), 
                        id_tipo: str = Form(...), 
                        nombre: str = Form(...), 
                        descripcion: str = Form(...), 
                        categoria: str = Form(...), 
                        dimensiones: str = Form(...), 
                        peso : str = Form(...),
                        db: Session = Depends(get_db)):
    print("Poducto: ", id_producto)
    product = schemas.ProductCreate(id_producto=id_producto, 
                              id_artesano=id_artesano,
                              nombre=nombre, 
                              id_tipo=id_tipo,
                              descripcion=descripcion,
                              categoria=categoria, 
                              dimensiones=dimensiones, 
                              peso=peso)
    db_product = crudProducto.create_product(db, product=product.id_producto)
    print("Db producto: ", db_product)
    if db_product: 
        raise HTTPException(status_code=400, detail="Product already registered")
    db_product = crudProducto.get_product_by_id(db, db_product=product.id_producto)
    if db_product: 
        raise HTTPException(status_code=400, detail="Id already registered")
    crudProducto.create_product(db=db, product=product)
    return templates.TemplateResponse("crearProducto.html.jinja", {"request": request})

@app.get("/product/create/", response_class=HTMLResponse)
async def create_product_template(request: Request):
    return templates.TemplateResponse("crearProducto.html.jinja", {"request": request})

@app.post("/producto/update/{product_id}/", response_class=HTMLResponse)
async def update_producto(request: Request, product_id: int, 
                          nombre: str = Form(...), 
                          descripcion: str = Form(...), 
                          categoria: str = Form(...), 
                          dimensiones: str = Form(...), 
                          peso: str = Form(...), 
                          id_tipo: str = Form(...), 
                          db: Session = Depends(get_db)):
    product_update = schemas.ProductUpdate(
        nombre=nombre, descripcion=descripcion, categoria=categoria,
        dimensiones=dimensiones, peso=peso, id_tipo=id_tipo
    )
    crudProducto.update_product(db=db, product_id=product_id, product=product_update)
    return RedirectResponse("crearProducto.html.jinja", status_code=HTTP_303_SEE_OTHER)

@app.post("/producto/delete/{product_id}/", response_class=HTMLResponse)
async def delete_producto(request: Request, product_id: int, db: Session = Depends(get_db)):
    crudProducto.delete_product(db=db, product_id=product_id)
    return RedirectResponse("crearProducto.html.jinja", status_code=HTTP_303_SEE_OTHER)

 
#Resenas
@app.post("/resena/create", response_model=schemas.ReviewBase)
async def create_resena_post(#current_user: Annotated[schemas.ReviewBase, Depends(get_current_user)],
                        request: Request, 
                        id_resena: str = Form(...), id_producto: str= Form(...),
                        fecha_invencion: str= Form(...), creador: str= Form(...),
                        anios_produccion: str= Form(...), anecdotas: str= Form(...),
                        db: Session = Depends(get_db)):
    print("Review: ", id_resena)
    review = schemas.ReviewCreate(
                              id_resena=id_resena, 
                              id_producto=id_producto,
                              fecha_invencion=fecha_invencion,
                              creador=creador,
                              anios_produccion=anios_produccion,
                              anecdotas=anecdotas
                            )
    db_review = crudResena.create_resena(db, review= review.id_resena)
    print("Db type: ", db_review)
    if db_review: 
        raise HTTPException(status_code=400, detail="Review not already registered")
    db_review = crudResena.get_resena_by_id(db, review=review.id_resena)
    if db_review: 
        raise HTTPException(status_code=400, detail="Review already registered")
    crudResena.create_resena(db=db, review=review)
    return templates.TemplateResponse("homeNoIniciado.html.jinja", {"request": request})


@app.get("/resena/create/", response_class=HTMLResponse)
async def create_resena_template(request: Request):
    return templates.TemplateResponse("crearResena.html.jinja", {"request": request})


@app.post("/resena/update/{resena_id}/", response_class=HTMLResponse)
async def update_resena(request: Request, resena_id: int, 
                        id_producto: int = Form(...), fecha_inversion: str = Form(...), 
                        creador: str = Form(...), anios_produccion: str = Form(...), 
                        anecdotas: str = Form(...), db: Session = Depends(get_db)):
    review_update = schemas.ReviewUpdate(
        id_producto=id_producto, fecha_inversion=fecha_inversion, creador=creador,
        anios_produccion=anios_produccion, anecdotas=anecdotas
    )
    crudResena.update_resena(db=db, resena_id=resena_id, resena=review_update)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

@app.post("/resena/delete/{resena_id}/", response_class=HTMLResponse)
async def delete_resena(request: Request, resena_id: int, db: Session = Depends(get_db)):
    crudResena.delete_resena(db=db, resena_id=resena_id)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

#Tipo Producto
@app.post("/type_product/create/", response_model=schemas.TypeProductBase)
async def create_tipo_producto_post(request: Request, nombre: str = Form(...), db: Session = Depends(get_db)):
    print("Tipo Product: ", nombre)
    type_product = schemas.TypeCreate(nombre=nombre)
    crudTipoProducto.create_type_product(db=db, type_product=type_product)
    types = crudTipoProducto.get_types(db)

    print('Lista tipos:', types)
    for type in types:
        print("Id:", type.id_tipo)
        print("Nombre:", type.nombre)
    return templates.TemplateResponse("listaTipoProducto.html.jinja", {"request": request, "typesProducts": types})


@app.get("/type_product/list", response_class=HTMLResponse, name="read_items")
async def read_types(request: Request, db: Session = Depends(get_db)):
    types = crudTipoProducto.get_types(db)
    return templates.TemplateResponse("listaTipoProducto.html.jinja", {"request": request, "typesProducts": types})


@app.get("/type_product/update/{type_id}/", response_class=HTMLResponse)
async def update_tipo_producto_template(request: Request, type_id: int, db: Session = Depends(get_db)):
    type_product = crudTipoProducto.get_type_by_id(db, type_id)
    return templates.TemplateResponse("modificarTipoProducto.html.jinja", {"request": request, "type_product": type_product})


# Ruta para obtener la plantilla de modificación
@app.get("/type_product/update/{type_id}/", response_class=HTMLResponse)
async def update_tipo_producto_template(request: Request, type_id: int, db: Session = Depends(get_db)):
    type_product = crudTipoProducto.get_type_by_id(db, type_id)
    return templates.TemplateResponse("modificarTipoProducto.html.jinja", {"request": request, "type_product": type_product})

# Ruta para manejar el POST de actualización
@app.post("/type_product/update/{type_id}/", response_class=HTMLResponse)
async def update_tipo_producto_post(
    request: Request, 
    type_id: int,  
    nombre: str = Form(...), 
    db: Session = Depends(get_db)
):
    type_update = schemas.TypeUpdate(id_tipo=type_id, nombre=nombre)
    crudTipoProducto.update_type_product(db=db, type_id=type_id, type=type_update)
    types = crudTipoProducto.get_types(db)
# Ruta para obtener la plantilla de modificación
@app.get("/type_product/update/{type_id}/", response_class=HTMLResponse)
async def update_tipo_producto_template(request: Request, type_id: int, db: Session = Depends(get_db)):
    type_product = crudTipoProducto.get_type_by_id(db, type_id)
    return templates.TemplateResponse("modificarTipoProducto.html.jinja", {"request": request, "type_product": type_product})

# Ruta para manejar el POST de actualización
@app.post("/type_product/update/{type_id}/", response_class=HTMLResponse)
async def update_tipo_producto_post(
    request: Request, 
    id_tipo: int,  
    nombre: str = Form(...), 
    db: Session = Depends(get_db)
):
    type_update = schemas.TypeUpdate(type_id=id_tipo, nombre=nombre)
    crudTipoProducto.update_type_product(db=db, type_id=id_tipo, type=type_update)
    types = crudTipoProducto.get_types(db)
    return templates.TemplateResponse("listaTipoProducto.html.jinja", {"request": request, "typesProducts": types})


@app.get("/type_product/create/", response_class=HTMLResponse)
async def create_tipo_producto_template(request: Request):
    return templates.TemplateResponse("crearTipoProducto.html.jinja", {"request": request})



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



