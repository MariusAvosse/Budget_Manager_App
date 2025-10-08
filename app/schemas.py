from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# === Auth ===
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# === Transactions ===
class TransactionBase(BaseModel):
    title: str
    amount: float
    type: str
    category: str

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True
