from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "demo-secret-key-for-interview")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class TokenData(BaseModel):
    email: str
    family_office_id: int


# Hardcoded demo users for interview
DEMO_USERS = {
    "smith@demo.com": {
        "password": "demo123",
        "family_office_id": 1,
        "name": "Smith Family Office Admin"
    },
    "jones@demo.com": {
        "password": "demo123", 
        "family_office_id": 2,
        "name": "Jones Family Office Admin"
    }
}


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("email")
        family_office_id: int = payload.get("family_office_id")
        
        if email is None or family_office_id is None:
            raise credentials_exception
            
        return TokenData(email=email, family_office_id=family_office_id)
    except JWTError:
        raise credentials_exception


def authenticate_user(email: str, password: str) -> Optional[dict]:
    if email in DEMO_USERS and DEMO_USERS[email]["password"] == password:
        return DEMO_USERS[email]
    return None