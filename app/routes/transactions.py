# app/routes/transactions.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def placeholder_transactions():
    return {"message": "Transactions endpoint en construction"}
