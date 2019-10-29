from fastapi import APIRouter
from datetime import timedelta
from fastapi import Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from daqbroker.web.classes import Token
from daqbroker.web.routes.utils import get_current_user, OAuth2PasswordRequestForm, authenticate_user, create_access_token
from daqbroker.storage.local_settings import User

ACCESS_TOKEN_EXPIRE_MINUTES = 30
#ACCESS_TOKEN_EXPIRE_SECONDS = 10

app = APIRouter()

#db_obj = get_database()
users_db = {}

@app.post("/token", response_model = Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta = access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/test_token")
async def test_access_token(current_user: User = Depends(get_current_user)):
    return True

