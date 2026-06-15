from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True)
    name: str  
    email: str = Field(unique=True, index=True)
    password_hash: str
    is_active: bool = Field(default=True)

