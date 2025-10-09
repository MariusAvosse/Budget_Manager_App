from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app import config

# ✅ Contexte sécurisé pour le hachage de mots de passe
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str):
    """Hache un mot de passe avec bcrypt (limité à 72 caractères)"""
    password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Vérifie la correspondance entre mot de passe et hash"""
    plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Crée un JWT signé avec date d’expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt
