import os
import jwt
from jwt import PyJWTError
from pathlib import Path
from datetime import datetime, timedelta
from secrets import token_hex
from fastapi import Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from daqbroker.web.utils import verify_password
from daqbroker.storage import session
from daqbroker.storage.local_settings import User
from daqbroker.storage.utils import get_local_resource, get_local_by_attr

from daqbroker.web.classes import TokenData, ConnectionInput

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_secret_key():
	file_path = Path(__file__).parent / 'secret.key'
	if os.path.isfile(file_path):
		with open(file_path, 'r') as fh:
			key = fh.read()
	else:
		key = token_hex(32)
		with open(file_path, 'w') as fh:
			fh.write(key)
	return key

def authenticate_user(db, username: str, password: str, level: int = 0):
	user = get_local_by_attr(db= session, Resource= User, attr_name= "username", attr_val= username)
	if not user:
		return False
	if not verify_password(user.password, password):
		return False
	return user

def create_access_token(*, data: dict, expires_delta: timedelta = None):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(minutes=15)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, get_secret_key(), ALGORITHM)
	return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
	credentials_exception = HTTPException(
		status_code=HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
		username: str = payload.get("sub")
		if username is None:
			raise credentials_exception
		token_data = TokenData(username=username)
	except PyJWTError as e:
		if type(e) == jwt.exceptions.ExpiredSignatureError:
			credentials_exception.detail = "Token expired"
		raise credentials_exception
	user = get_local_by_attr(db= session, Resource= User, attr_name= "username", attr_val= username)
	if user is None:
		raise credentials_exception
	return user

def make_url(conn: ConnectionInput):
	print("MAKING CONNECTION URL")

def test_connection(conn: ConnectionInput):
	print("AM TESTING", ConnectionInput.dict())

