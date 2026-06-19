import os
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
EXPIRE = int(os.getenv("JWT_EXPIRE_HOURS"))


def create_access_token(user_id: int):

    payload = {"sub": str(user_id), "exp": datetime.now(UTC) + timedelta(hours=EXPIRE)}
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    return token

def decode_token(token: str):       

    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            return None
        
        return int(user_id)
              
    except JWTError:      
        return None   
 
  
def create_reset_token(user_id: int):

    jti = str(uuid4())
    payload = {"sub": str(user_id), "jti": jti, "type": "password_reset", "exp": datetime.now(UTC) + timedelta(minutes=30)}
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    return token, jti

def decode_reset_token(token: str):       
    
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM]) 

        if payload.get("type") != "password_reset":          
            return None

        user_id = payload.get("sub")     
        jti = payload.get("jti")   

        if not user_id or not jti:
            return None
        
        return {"user_id": int(user_id), "jti": jti}
              
    except JWTError:        
        return None   
    

def create_verify_email_token(name: str, email: str, password_hash: str):

    jti = str(uuid4())
    payload = {"sub": email, "name": name, "password_hash": password_hash, "jti": jti, "type": "verify_email", "exp": datetime.now(UTC) + timedelta(minutes=30)}
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    return token, jti

def decode_verify_email_token(token: str):

    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])

        if payload.get("type") != "verify_email":
            return None

        return payload

    except JWTError:
        return None

