from fastapi import Depends, FastAPI, File, Request, HTTPException, Form, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
import crudUsuario, crudProducto, crudResena, crudTipoProducto, models, schemas
from seguridad.manejarToken import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_user
import crudUsuario, models, schemas, crudProducto
from sqlApp.database import SessionLocal, engine
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from fastapi import Depends
from typing import Annotated, Optional, Union
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
                          categoria: str = Form(...), 
                          dimensiones: str = Form(...), 
                          peso: str = Form(...), 
                          id_tipo: str = Form(...), 
                          db: Session = Depends(get_db)):
    product_update = schemas.ProductUpdate(
        id_producto=id_producto,
        nombre=nombre, descripcion=descripcion, categoria=categoria,
        dimensiones=dimensiones, peso=peso, id_tipo=id_tipo
    )
    crudProducto.update_product(db=db, product_id=id_producto, product=product_update)
    products = crudProducto.get_products(db)
    return templates.TemplateResponse("listaProducto.html.jinja", {"request": request, "Products": products})


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
    products = crudProducto.get_product_by_id(db, product_id)
    return templates.TemplateResponse("modificarProducto.html.jinja", {"request": request, "Products": products})

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
                        anios_produccion: str= Form(...), anecdotas: str= Form(...),
                        db: Session = Depends(get_db)):

    review = schemas.ReviewCreate(
                              id_producto=id_producto,
                              fecha_invencion=fecha_invencion,
                              creador=creador,
                              anios_produccion=anios_produccion,
                              anecdotas=anecdotas
                            )
    crudResena.create_resena(db, resena= review)
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

@app.get("/type_product/list", response_class=HTMLResponse, name="read_items")
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




