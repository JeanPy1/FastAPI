from pydantic import BaseModel
    
class User(BaseModel): 
    name: str
    email: str
    password: str
    active: bool = True
    
class Login(BaseModel):
    email: str
    password: str

class Register(BaseModel):
    name: str
    email: str
    password: str

class ResetPassword(BaseModel):
    token: str
    new_password: str

class ForgotPassword(BaseModel):
    email: str