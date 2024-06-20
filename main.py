from fastapi import Depends, FastAPI, Request, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import crudUsuario, crudProducto, crudResena, crudTipoProducto, models, schemas
from seguridad.manejarToken import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_user
from sqlApp.database import SessionLocal, engine
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER
from fastapi import Depends
from typing import Annotated, Union

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


#Producto
@app.post("/producto/create/", response_model=schemas.ProductBase,)
async def create_product_post(current_user: Annotated[schemas.UserBase, Depends(get_current_user) ],
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
    return templates.TemplateResponse("homeNoIniciado.html.jinja", {"request": request})

@app.get("/product/create/", response_class=HTMLResponse)
async def create_product_template(request: Request):
    return templates.TemplateResponse("crearProducto.html.jinja", {"request": request})

 
#Resenas
@app.post("/resena/create", response_model=schemas.ReviewCreate)
async def create_resew_post(current_user: Annotated[schemas.ReviewBase, Depends(get_current_user)],
                        request: Request, 
                        id_resena: str = Form(...), 
                        id_producto: str= Form(...),
                        fecha_invencion: str= Form(...),
                        creador: str= Form(...),
                        anios_produccion: str= Form(...),
                        anecdotas: str= Form(...),
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


#Tipo Producto
@app.post("/type_product/create", response_model=schemas.TipoUserBase)
async def create_type_product_post(current_user: Annotated[schemas.UserBase, Depends(get_current_user)],
                        request: Request, 
                        nombre: str = Form(...), 
                        id_tipo: str= Form(...),
                        db: Session = Depends(get_db)):
    print("Tipo Product: ", nombre)
    type_product = schemas.TipoCreate(
                              nombre=nombre, 
                              id_tipo=id_tipo
                            )
    db_type = crudTipoProducto.create_type_product(db, type_product= type_product.nombre)
    print("Db type: ", db_type)
    if db_type: 
        raise HTTPException(status_code=400, detail="Type not already registered")
    db_type = crudTipoProducto.get_type_by_name(db, db_type=type_product.nombre)
    if db_type: 
        raise HTTPException(status_code=400, detail="Type already registered")
    crudTipoProducto.create_type_product(db=db, type_product=type_product)
    return templates.TemplateResponse("homeNoIniciado.html.jinja", {"request": request})




