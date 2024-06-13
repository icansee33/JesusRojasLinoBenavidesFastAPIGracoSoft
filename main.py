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

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print("Users: ", user)
    db_user = crud.get_user_by_email(db, email=user.email)
    print("Db user: ", db_user)
    if db_user: 
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)
