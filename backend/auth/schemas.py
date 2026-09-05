from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    class Config:
        from_attributes = True

Token.model_rebuild()
