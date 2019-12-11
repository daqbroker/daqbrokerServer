import os
import jwt
import threading
from jwt import PyJWTError
from pathlib import Path
from datetime import datetime, timedelta
from secrets import token_hex
from fastapi import Depends, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_503_SERVICE_UNAVAILABLE
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from typing import Optional, AsyncIterable

from sqlalchemy.engine import Engine as Database
from sqlalchemy.orm import Session

from daqbrokerServer.web.utils import verify_password
# from daqbrokerServer.storage import session_open, local_engine
from daqbrokerServer.storage.local_schema import User, Connection
from daqbrokerServer.storage.utils import get_local_resources
from daqbrokerServer.web.classes.token import TokenData

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

local_session = None

async def get_db_conn():
	assert local_session is not None
	return local_session


# This is the part that replaces sessionmaker
async def get_db(db_conn = Depends(get_db_conn)):
	try:
		sess = db_conn.session # Session(bind= local_session.engine)
		yield sess
	finally:
		sess.remove()

async def get_db_folder(db_conn = Depends(get_db_conn)):
	return db_conn.db_folder

# def get_db(request: Request):
# 	keys = ["db_folder"]
# 	args = {}

# 	#for key in keys:
# 	#	args[key] = getattr(request.state, key) if hasattr(request.state, key) else None
# 	#local_session = LocalSession(**args)
# 	#local_session.setup()
# 	#sess = request.state.local_session()
# 	return request.state.local_session
# 	#print("DEPENDENCY", threading.get_ident(), sess)
# 	#yield sess
# 	#print("DEPENDENCY DONE", threading.get_ident(), sess)
# 	#sess.close()

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
	user = get_local_resources(db= db, Resource= User, key_vals= { "username":username }).first()
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

async def get_current_user(token: str = Depends(oauth2_scheme), session= Depends(get_db)):
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
	# with session_open(local_engine) as session:
	user = get_local_resources(db=session, Resource= User, key_vals= { "username":username }).first()
	if user is None:
		raise credentials_exception
	return user

def get_user(db, username: str, status_code: int, err_msg: str = "", find= True):
	user = get_local_resources(db=db, Resource= User, key_vals= { "username":username }).first()
	exception = HTTPException(
		status_code=status_code,
		detail=err_msg,
	)
	if find:
		if not user:
			raise exception
		return user
	else:
		if user:
			raise exception
		return None

def get_connection(db, conn_id: int, status_code: int ,err_msg: str = "", find= True):
	connection = get_local_resources(db=db, Resource= Connection, r_id=conn_id)
	exception = HTTPException(
		status_code=status_code,
		detail=err_msg
	)
	if find:
		if not connection:
			raise exception
		return connection
	else:
		if connection:
			raise exception
		return None

def test_connection(connection: Connection):
	exception = HTTPException(
		status_code=HTTP_503_SERVICE_UNAVAILABLE,
		detail="",
	)
	if connection.connectable:
		return True
	else:
		exception.detail = new_connection.conn_error
		raise exception

def add_campaign(connection: Connection, campaign: str):
	exception = HTTPException(
		status_code=HTTP_409_CONFLICT,
		detail="A campaign with that name already exists",
	)
	test_connection(connection)
	if campaign in connection.campaigns:
		raise exception
	if len(campaign) > 30:
		exception.status_code=HTTP_422_UNPROCESSABLE_ENTITY
		exception.detail="A campaign identifier must be no longer than 30 characters"
		raise exception
	if not "".join(campaign.split("_")).isalnum():
		exception.status_code=HTTP_422_UNPROCESSABLE_ENTITY
		exception.detail="A campaign identifier must not contain special characters (only '_' are allowed)"
		raise exception
	db_name = "daqbroker_" + campaign
	connection.create_database(db_name)
	connection.get_databases()
	return connection.campaigns

def remove_campaign(connection: Connection, campaign: str):
	exception = HTTPException(
		status_code=HTTP_404_NOT_FOUND,
		detail="Campaign does not exist on connection with id='" + str(connection.id) + "'"
	)
	if campaign in connection.campaigns: # Assuming connection is loaded from database, this is reasonable
		db_name = "daqbroker_" + campaign
		connection.remove_database(db_name)
		connection.get_databases()
		return connection.campaigns
	raise exception

class AuthUser:

	def __init__(self, test_level: int = 0):
		self.test_level = test_level

	async def __call__(self, user: User = Depends(get_current_user),):
		if user.type < self.test_level:
			raise HTTPException(
				status_code=HTTP_401_UNAUTHORIZED,
				detail="You do not have permission to access this resource",
				headers={"WWW-Authenticate": "Bearer"},
			)
		return user

