from fastapi import APIRouter
from daqbroker.services.web.api.auth import app as auth

app = APIRouter()

app.include_router(
	auth,
	prefix="/auth",
	tags=["auth"],
	responses={404: {"description": "Not found"}}
)

@app.get("/test")
async def read_root():
	return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
	return {"item_id": item_id, "q": q}


