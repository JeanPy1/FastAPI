from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, Cookie, Depends
from sqlmodel import Session, select
from database.session import get_session
from schemas.auth import Login, Register, ForgotPassword, ResetPassword
from models.user import User
from security.jwt import create_access_token, decode_token, create_reset_token, decode_reset_token, create_verify_email_token, decode_verify_email_token
from security.password import hash_password, verify_password
from mail.send import send_reset_email, send_verify_email
from jose import JWTError
from os import getenv

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/me")
def me(access_token: str | None = Cookie(default=None), session: Session = Depends(get_session)):
   
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
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Debes verificar tu correo antes de iniciar sesión")

    token = create_access_token(user.id)

    response.set_cookie(key="access_token", path="/", value=token, httponly=True,secure=True,  samesite="none", max_age=60 * 60 * 24)

    return {"message": "Inicio de sesión correcto"}



@router.post("/register")
def register(data: Register, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):

    existing_user = session.exec(select(User).where(User.email == data.email)).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="El correo ya existe")       
    
    password_hash = hash_password(data.password)

    token, jti = create_verify_email_token(name=data.name, email=data.email, password_hash=password_hash)

    user = User(name=data.name, email=data.email, password_hash=password_hash, is_active=False, verify_jti=jti)

    session.add(user)
    session.commit()
    
    verify_link = (
        f"{getenv('FRONTEND_URL')}"
        f"/verify-email?token={token}"
    )

    background_tasks.add_task(send_verify_email, data.email, verify_link)   

    return {"message": "Hemos enviado un correo de verificación"}

@router.get("/verify-email")
def verify_email(token: str, session: Session = Depends(get_session)):

    payload = decode_verify_email_token(token)

    if not payload:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    user = session.exec(select(User).where(User.email == payload["sub"])).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if user.is_active:
        raise HTTPException(status_code=409, detail="La cuenta ya fue verificada")
    
    if user.verify_jti != payload["jti"]:
        raise HTTPException(status_code=400, detail="Este enlace ya no es valido")
    
    user.is_active = True
    user.verify_jti = None    

    session.add(user)
    session.commit()

    return {"message": "Cuenta verificada correctamente"}



@router.post("/forgot-password")
def forgot_password(data: ForgotPassword, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):

    user = session.exec(select(User).where(User.email == data.email)).first()   

    if user and user.is_active:        

        token, jti = create_reset_token(user.id)

        user.verify_jti = jti

        session.add(user)
        session.commit()       

        reset_link = (
            f"{getenv('FRONTEND_URL')}"
            f"/reset?token={token}"
        )

        background_tasks.add_task(send_reset_email, user.email, reset_link)

    return {"message": "Si el correo existe, se envió un enlace de recuperación"}

@router.get("/validate-reset-token")
def validate_reset_token(token: str, session: Session = Depends(get_session)):

    try:
        data = decode_reset_token(token)  

        if not data:
            raise HTTPException(status_code=400, detail="invalid_token")
        
        user = session.get(User, data["user_id"])

        if not user:
            raise HTTPException(status_code=404, detail="user_not_found")
        
        if user.verify_jti is None:
            raise HTTPException(status_code=400, detail="token_used")

        if user.verify_jti != data["jti"]:
            raise HTTPException(status_code=400, detail="token_replaced")
      
        return {"valid": True}

    except JWTError:
        raise HTTPException(status_code=400, detail="token_expired")
    
@router.post("/reset-password")
def reset_password(data: ResetPassword, session: Session = Depends(get_session)):

    try:
        token_data = decode_reset_token(data.token)       

        if not token_data:
            raise HTTPException(status_code=400, detail="Token inválido")

    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
   
    user = session.get(User, token_data["user_id"])

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if user.verify_jti != token_data["jti"]:
        raise HTTPException(status_code=400, detail="Este enlace ya no es válido")

    user.password_hash = hash_password(data.new_password)

    user.verify_jti = None

    session.add(user)
    session.commit()

    return {"message": "Contraseña actualizada"}



@router.post("/logout")
def logout(response: Response):

    response.delete_cookie(key="access_token", path="/", secure=True,  samesite="none")

    return {"message": "Logout correcto"}







