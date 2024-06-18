@app.post("/usuario/create/", response_class=HTMLResponse)
def create_usuario_post(cedula_identidad: str = Form(...), 
                        nombre: str = Form(...), 
                        apellido: str = Form(...), 
                        fecha_nacimiento: str = Form(...), 
                        direccion: str = Form(...), 
                        correo_electronico: str = Form(...), 
                        contrasena: str = Form(...), 
                        tipo_usuario: str = Form(...),
                        db: Session = Depends(get_db),
                        request: Request):
    print("Usuario: ", correo_electronico)
    user = schemas.UserCreate(
        cedula_identidad=cedula_identidad, 
        nombre=nombre, 
        apellido=apellido, 
        fecha_nacimiento=fecha_nacimiento, 
        direccion=direccion,
        correo_electronico=correo_electronico, 
        contrasena=contrasena, 
        tipo_usuario=tipo_usuario
    )
    
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
