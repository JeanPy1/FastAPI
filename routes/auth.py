from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, Cookie, Depends
from sqlmodel import Session, select
from database.session import get_session
from schemas.auth import Login, Register, ForgotPassword, ResetPassword
from models.user import User
from security.jwt import create_access_token, decode_token, create_reset_token, decode_reset_token
from security.password import hash_password, verify_password
from mail.send import send_reset_email
from jose import JWTError
from os import getenv


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me")
def me(access_token: str | None = Cookie(default=None), session: Session = Depends(get_session)):

    print(access_token)
    if not access_token:
        raise HTTPException(status_code=401, detail="no autenticado")
    
    user_id = decode_token(access_token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalido")
    
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return {"id": user.id, "name": user.name, "email": user.email}


@router.post("/login")
def login(data: Login, response: Response, session: Session = Depends(get_session)):

    user = session.exec(select(User).where(User.email == data.email)).first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token(user.id)

    response.set_cookie(key="access_token", value=token, httponly=True, samesite="none", secure=True, max_age=60 * 60 * 24)

    print(token)

    return {"message": "Login correcto"}


@router.post("/register")
def register(data: Register, session: Session = Depends(get_session)):

    existing_user = session.exec(select(User).where(User.email == data.email)).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="El correo ya existe")       
    
    user = User(name=data.name, email=data.email, password_hash=hash_password(data.password))

    session.add(user)
    session.commit()

    return {"message": "Usuario creado correctamente"}


@router.post("/forgot-password")
def forgot_password(data: ForgotPassword, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):

    user = session.exec(select(User).where(User.email == data.email)).first()
    
    if user:
        token = create_reset_token(user.id)
        reset_link = (
            f"{getenv('FRONTEND_URL')}"
            f"/reset?token={token}"
        )

        background_tasks.add_task(send_reset_email, user.email, reset_link)

    return {"message": "Si el correo existe, se envió un enlace de recuperación"}


@router.get("/validate-reset-token")
def validate_reset_token(token: str):

    try:
        user_id = decode_reset_token(token)  

        if not user_id:
            raise HTTPException(status_code=400, detail="Token inválido")
      
        return {"valid": True}

    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    

@router.post("/reset-password")
def reset_password(data: ResetPassword, session: Session = Depends(get_session)):

    try:
        user_id = decode_reset_token(data.token)       

        if not user_id:
            raise HTTPException(status_code=400, detail="Token inválido")

    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
   
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.password_hash = hash_password(data.new_password)

    session.add(user)
    session.commit()

    return {"message": "Contraseña actualizada"}


@router.post("/logout")
def logout(response: Response):

    response.delete_cookie(key="access_token", path="/", samesite="none", secure=True)

    return {"message": "Logout correcto"}







