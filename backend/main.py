from fastapi import FastAPI
from sqlalchemy import text

from database import engine

app = FastAPI(title="Finance App")