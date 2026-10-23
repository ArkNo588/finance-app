from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import Token
from security import DUMMY_HASH, create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form.username.strip().lower()
    user = db.scalars(select(User).where(User.email == email)).first()

    # On vérifie toujours un hash, même si l'email n'existe pas,
    # pour que le temps de réponse ne révèle pas quels emails existent.
    hashed = user.hashed_password if user else DUMMY_HASH
    password_ok = verify_password(form.password, hashed)

    if user is None or not password_ok:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}