from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserInDB(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: EmailStr
    hashed_password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr