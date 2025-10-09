from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

from app import models, schemas, config
from app.database import SessionLocal

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# --- Dépendance DB ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Décoder le token et récupérer l'utilisateur ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# --- CRUD Transactions ---

#  Créer une transaction
@router.post("/", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_transaction = models.Transaction(**transaction.dict(), owner_id=current_user.id)
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


#  Lister les transactions de l'utilisateur
@router.get("/", response_model=list[schemas.Transaction])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.owner_id == current_user.id)
        .order_by(models.Transaction.created_at.desc())
        .all()
    )
    return transactions


#  Modifier une transaction
@router.put("/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(
    transaction_id: int,
    updated: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transaction = (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id, models.Transaction.owner_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    for key, value in updated.dict().items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)
    return transaction


#  Supprimer une transaction
@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transaction = (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id, models.Transaction.owner_id == current_user.id)
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    db.delete(transaction)
    db.commit()
    return {"message": "Transaction supprimée"}

# Statistiques de budget
@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.owner_id == current_user.id)
        .all()
    )

    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    balance = total_income - total_expense

    # Calcul par catégorie
    categories = {}
    for t in transactions:
        categories.setdefault(t.category, {"income": 0, "expense": 0})
        categories[t.category][t.type] += t.amount

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "by_category": categories,
    }
