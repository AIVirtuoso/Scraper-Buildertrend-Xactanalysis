from fastapi import FastAPI, APIRouter
import os
from dotenv import load_dotenv

from app.Utils.scraping import run_scraper

from pydantic import BaseModel

load_dotenv()

class AuthModel(BaseModel):
    builder_user: str
    builder_pass: str
    xact_user: str
    xact_pass: str

router = APIRouter()

@router.post('/notification')
def get_notification(auth: AuthModel):
    print("start")
    print(auth.builder_user, auth.builder_pass, auth.xact_user, auth.xact_pass)
    return run_scraper(auth.builder_user, auth.builder_pass, auth.xact_user, auth.xact_pass)