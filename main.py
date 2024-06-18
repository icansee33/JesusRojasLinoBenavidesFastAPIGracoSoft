from fastapi import Depends, FastAPI, Request, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import crud, models, schemas
from sqlApp.database import SessionLocal, engine
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER
from fastapi import Depends


from datetime import datetime

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
async def create_usuario_post(request: Request, cedula_identidad: str = Form(...), 
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
    db_user = crud.get_user_by_email(db, email=user.correo_electronico)
    print("Db user: ", db_user)
    if db_user: 
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.get_user_by_ci(db, user_id=user.cedula_identidad)
    if db_user: 
        raise HTTPException(status_code=400, detail="CI already registered")
    print("Hasta acá va bien")
    crud.create_user(db=db, user=user)
    return templates.TemplateResponse("crearUsuario.html.jinja", {"request": request})


@app.get("/usuario/create/", response_class=HTMLResponse)
async def create_usuario_template(request: Request):
    print("Usuario get: ", )
    return templates.TemplateResponse("crearUsuario.html.jinja", {"request": request})



        

"""
@app.post("/usuario/", response_model=schemas.User)
def create_usuario(usuario: schemas.UserCreate, db: Session = Depends(get_db)):
    # Force the user type to "Cliente"
    usuario_dict = usuario.dict()
    usuario_dict['tipo_usuario'] = "Cliente"
    usuario_con_cliente = schemas.UserCreate(**usuario_dict)
    
    # Check if the email or cedula already exists
    db_usuario = crud.get_user_by_email(db, correo_electronico=usuario.correo_electronico)
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_usuario = crud.get_user_by_ci(db, cedula_identidad=usuario.cedula_identidad)
    if db_usuario:
        raise HTTPException(status_code=400, detail="Cedula already registered")
    
    return crud.create_user(db=db, usuario=usuario_con_cliente)

"""





@app.get("/", response_class=HTMLResponse)
async def home_no_iniciado(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("homeNoIniciado.html.jinja", {"request": request})


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def read_usuario(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = crud.get_user_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("perfilUsuario.html", {"request": request, "item": item})


@app.get("/usuario/update/{user_id}/", response_class=HTMLResponse)
async def update_usuario_form(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("modificarUsuario.html.jinja", {"request": request, "item": item})

@app.post("/usuario/update/{user_id}/", response_class=HTMLResponse)
async def update_item(request: Request, item_id: int, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    usuario_update = schemas.UserUpdate(name=name, description=description)
    crud.update_item(db=db, item_id=item_id, item=usuario_update)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

@app.post("/usuario/delete/{user_id}", response_class=HTMLResponse)
async def delete_usuario(request: Request, item_id: int, db: Session = Depends(get_db)):
    crud.delete_item(db=db, item_id=item_id)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

# Iniciar sesión
@app.get("/iniciarsesion", response_class=HTMLResponse)
async def iniciar_sesion(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("iniciarSesion.html.jinja", {"request": request})
