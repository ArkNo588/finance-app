import getpass
import sys

from sqlalchemy import select

from database import SessionLocal
from models import User
from security import hash_password

email = input("Email : ").strip().lower()
password = getpass.getpass("Mot de passe (12 caractères min.) : ")
confirm = getpass.getpass("Confirmer : ")

if password != confirm:
    sys.exit("Les mots de passe ne correspondent pas.")
if len(password) < 12:
    sys.exit("Mot de passe trop court.")

with SessionLocal() as db:
    if db.scalars(select(User).where(User.email == email)).first():
        sys.exit("Cet utilisateur existe déjà.")
    db.add(User(email=email, hashed_password=hash_password(password)))
    db.commit()
    print("Utilisateur créé.")