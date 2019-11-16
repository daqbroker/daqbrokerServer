from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY

from daqbrokerServer.web.routes.utils import get_current_user, Depends, HTTPException, oauth2_scheme

from daqbrokerServer.storage import session
from daqbrokerServer.storage.local_settings import User, Connection
from daqbrokerServer.web.classes.user import User as UserData, UserInput
from daqbrokerServer.web.classes.connection import Connection as ConnectionData
from daqbrokerServer.storage.utils import get_local_resources, add_local_resource, delete_local_resource
from daqbrokerServer.web.routes.utils import get_user, get_connection

app = APIRouter()

@app.get("/")
async def get_users(current_user: User = Depends(get_current_user)):
	current_user.test_security(level=2)
	return [user.username for user in get_local_resources(db= session, Resource= User).all()]

@app.get("/{username}", response_model=UserData)
async def get_single_user(username: str, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=2)
	return get_user(username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")

@app.get("/{username}/connections", response_model=List[ConnectionData])
async def get_user_connections(username: str, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=2)
	user = get_user(username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
	return [connection for connection in user.connections]

@app.post("/", response_model=UserData)
async def add_user(new_user: UserInput, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	user = get_user(new_user.username, HTTP_409_CONFLICT, err_msg="User '" + new_user.username + "' already exists", find=False)
	return add_local_resource(db= session, Resource= User, user_input= new_user)

@app.post("/{username}/connections", response_model=List[ConnectionData])
async def add_user_connection(conn_ids: List[int], username: str, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	user = get_user(username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
	for conn_id in conn_ids:
		connection  = get_connection(conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
		conn_exists = [connection for connection in user.connections if connection.id == conn_id]
		if len(conn_exists) < 1: # Should I instead raise an exception here?
			user.connections.append(connection)
		#raise HTTPException(
		#	status_code=HTTP_409_CONFLICT,
		#	detail="Connection with id='" + str(conn_id) + "' already exists in user '" + username + "'"
		#)
	session.commit()
	return [connection for connection in user.connections]

@app.put("/{username}", response_model=UserData)
async def change_user(username: str, new_data : UserInput, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	to_check = ["username", "email"]
	users = [user for user in get_local_resources(db= session, Resource= User).all()]
	user = get_user(username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
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
	current_user.test_security(level=3)
	user = get_user(username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
	return delete_local_resource(db= session, Resource= User, instance= user)

@app.delete("/{username}/connections/", response_model=List[ConnectionData])
async def remove_user(username: str, conn_ids: List[int], current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	user = get_user(username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
	to_delete = []
	for conn_id in conn_ids:
		connection  = get_connection(conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
		conn_exists = [connection for connection in user.connections if connection.id == conn_id]
		if len(conn_exists) > 0:
			to_delete.append(conn_exists[0])
			user.connections.remove(conn_exists[0])
	session.commit()
	return to_delete