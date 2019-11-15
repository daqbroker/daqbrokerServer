from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY

from daqbrokerServer.web.routes.utils import get_current_user, Depends, HTTPException, oauth2_scheme

from daqbrokerServer.storage import session
from daqbrokerServer.storage.local_settings import User
from daqbrokerServer.web.classes import User as UserData
from daqbrokerServer.web.classes import UserInput
from daqbrokerServer.storage.utils import get_local_resources, add_local_resource, delete_local_resource

app = APIRouter()

@app.get("/")
async def get_users(current_user: User = Depends(get_current_user)):
	current_user.test_security(level=2)
	return [user.username for user in get_local_resources(db= session, Resource= User).all()]

@app.get("/{username}", response_model=UserData)
async def get_users(username: str, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=2)
	user = get_local_resources(db= session, Resource= User, key_vals= { "username":username }).first()
	#user = User(db= users_db, username= username).get()
	if not user:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
			detail="User " + username + " not found",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return user

@app.post("/", response_model=UserData)
async def add_user(new_user: UserInput, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=2)
	user = get_local_resources(db= session, Resource= User, key_vals={ "username":new_user.username }).first()
	if user:
		raise HTTPException(
			status_code=HTTP_409_CONFLICT,
			detail="User '" + new_user.username + "' already exists",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return add_local_resource(db= session, Resource= User, user_input= new_user)

@app.put("/{username}", response_model=UserData)
async def change_user(username: str, new_data : UserInput, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=2)
	to_check = ["username", "email"]
	users = [user for user in get_local_resources(db= session, Resource= User).all()]
	user = get_local_resources(db= session, Resource= User, key_vals={ "username":username }).first()
	exception = HTTPException(
		status_code=HTTP_404_NOT_FOUND,
		detail="User '" + username + "' not found",
		headers={"WWW-Authenticate": "Bearer"},
	)
	if not user:
		raise exception
	for attr in to_check: # Maybe put this in another function
		attr_check = [getattr(user_check, attr) for user_check in users]
		if getattr(new_data, attr) != getattr(user, attr) and getattr(new_data, attr) in attr_check:
			status_code=HTTP_409_CONFLICT,
			exception.detail = attr + " with value '" + getattr(user, attr) + "' already exists"
			raise exception
	return add_local_resource(db= session, Resource= User, user_input= new_data, r_id=user.id)

@app.delete("/{username}", response_model=UserData)
async def remove_user(username: str, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=2)
	user = get_local_resources(db= session, Resource= User, key_vals={ "username":username }).first()
	if not user:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
			detail="User '" + username + "' not found",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return delete_local_resource(db= session, Resource= User, instance= user)

