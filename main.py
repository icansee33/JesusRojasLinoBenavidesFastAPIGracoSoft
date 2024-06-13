from fastapi import Depends, FastAPI, Request, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import crud, models, schemas
from sqlApp.database import SessionLocal, engine
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER
from fastapi import Depends


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


        
"""

@app.post("/usuario/create", response_model=schemas.User)
def create_usuario(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print("Usuario: ", user)
    db_user = crud.get_user_by_email(db, email=user.email)
    print("Db user: ", db_user)
    if db_user: 
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)



@app.get("/user/{item_id}", response_class=HTMLResponse)
async def read_usuario(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = crud.get_user_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse("item_detail.html", {"request": request, "item": item})

@app.get("/item/create/", response_class=HTMLResponse)
async def create_item_form(request: Request):
    return templates.TemplateResponse("item_create.html", {"request": request})

@app.post("/item/create/", response_class=HTMLResponse)
async def create_item(request: Request, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    item = schemas.ItemCreate(name=name, description=description)
    crud.create_item(db=db, item=item)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

@app.get("/item/edit/{item_id}/", response_class=HTMLResponse)
async def edit_item_form(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse("item_edit.html", {"request": request, "item": item})

@app.post("/item/edit/{item_id}/", response_class=HTMLResponse)
async def edit_item(request: Request, item_id: int, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    item_update = schemas.ItemUpdate(name=name, description=description)
    crud.update_item(db=db, item_id=item_id, item=item_update)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

@app.post("/item/delete/{item_id}", response_class=HTMLResponse)
async def delete_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    crud.delete_item(db=db, item_id=item_id)
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

"""