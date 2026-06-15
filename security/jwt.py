import os
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from dotenv import load_dotenv

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

    payload = {"sub": str(user_id), "type": "password_reset", "exp": datetime.now(UTC) + timedelta(minutes=30)}
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    return token

def decode_reset_token(token: str):       
    
    try:

        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM]) 

        if payload.get("type") != "password_reset":          
            return None

        user_id = payload.get("sub")        

        if not user_id:
            return None
        
        return int(user_id)
              
    except JWTError:        
        return None   