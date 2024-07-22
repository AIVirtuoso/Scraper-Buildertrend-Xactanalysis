from fastapi import FastAPI, APIRouter, BackgroundTasks
import os
from dotenv import load_dotenv

from app.Utils.scrape_xactanalysis import run_scraper as scrape_xactanalysis
from app.Utils.scrape_buildertrend import run_scraper as scrape_buildertrend
import asyncio
import aiohttp
from pydantic import BaseModel

load_dotenv()

class AuthModel(BaseModel):
    source: str
    builder_user: str
    builder_pass: str
    xact_user: str
    xact_pass: str

router = APIRouter()



@router.post('/notification')
async def get_notification(auth: AuthModel):
    print("start")
    print(auth.source, auth.builder_user, auth.builder_pass, auth.xact_user, auth.xact_pass)
    if auth.source == "BuilderTrend":
        task_builder = asyncio.create_task(scrape_buildertrend(auth.source, auth.builder_user, auth.builder_pass, auth.xact_user, auth.xact_pass))
        await task_builder
    else:
        
        task_xact = asyncio.create_task(scrape_xactanalysis(auth.source, auth.builder_user, auth.builder_pass, auth.xact_user, auth.xact_pass))
        await task_xact