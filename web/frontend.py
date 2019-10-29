from pathlib import Path
from fastapi import APIRouter
from starlette.staticfiles import StaticFiles

frontend = APIRouter()

frontend.mount("/static", StaticFiles(directory=str(Path(__file__).parent / 'frontend/dist')), name="static")