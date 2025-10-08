from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, transactions

app = FastAPI(title="Budget Manager API")

# Configuration CORS
origins = ["http://localhost:4200"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de gestion de budget"}