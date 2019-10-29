import asyncio
import uvicorn

from fastapi import FastAPI

from daqbroker.web.api import api

app = FastAPI()

app.include_router(api, prefix="/api")
