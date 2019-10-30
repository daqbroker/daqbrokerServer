import asyncio
import uvicorn

from fastapi import FastAPI

from daqbrokerServer.web.api import api

app = FastAPI()

app.include_router(api, prefix="/api")
