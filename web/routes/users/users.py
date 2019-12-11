import threading

from typing import List

from fastapi import APIRouter
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY


from daqbrokerServer.storage.local_schema import User, Connection
from daqbrokerServer.web.classes.user import User as UserData, UserInput
from daqbrokerServer.web.classes.connection import Connection as ConnectionData
from daqbrokerServer.storage.utils import get_local_resources, add_local_resource, delete_local_resource
from daqbrokerServer.web.routes.utils import get_user, get_connection, get_db, get_current_user, Depends, HTTPException, AuthUser

app = APIRouter()

@app.get("/", dependencies=[Depends(AuthUser(2))])
async def get_users(session= Depends(get_db)):
	return [user.username for user in get_local_resources(db= session, Resource= User).all()]

@app.get("/{username}", response_model=UserData, dependencies=[Depends(AuthUser(2))])
async def get_single_user(username: str, session= Depends(get_db)):
	user = get_user(session, username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
	return user

@app.get("/{username}/connections", response_model=List[ConnectionData], dependencies=[Depends(AuthUser(2))])
async def get_user_connections(username: str, current_user: User = Depends(get_current_user), session= Depends(get_db)):
	user = get_user(session, username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
	return [connection for connection in user.connections]

@app.post("/", response_model=UserData, dependencies=[Depends(AuthUser(2))])
async def add_user(new_user: UserInput, current_user: User = Depends(get_current_user), session= Depends(get_db)):
	user = get_user(session, new_user.username, HTTP_409_CONFLICT, err_msg="User '" + new_user.username + "' already exists", find=False)
	return add_local_resource(db= session, Resource= User, user_input= new_user)

@app.post("/{username}/connections", response_model=List[ConnectionData], dependencies=[Depends(AuthUser(2))])
async def add_user_connections(conn_ids: List[int], username: str, current_user: User = Depends(get_current_user), session= Depends(get_db)):
	user = get_user(session, username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
	for conn_id in conn_ids:
		connection  = get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
		conn_exists = [connection for connection in user.connections if connection.id == conn_id]
		if len(conn_exists) < 1: # Should I instead raise an exception here?
			user.connections.append(connection)
		#raise HTTPException(
		#	status_code=HTTP_409_CONFLICT,
		#	detail="Connection with id='" + str(conn_id) + "' already exists in user '" + username + "'"
		#)
	session.commit()
	return [connection for connection in user.connections]

@app.put("/{username}", response_model=UserData, dependencies=[Depends(AuthUser(2))])
async def change_user(username: str, new_data : UserInput, current_user: User = Depends(get_current_user), session= Depends(get_db)):
	to_check = ["username", "email"]
	users = [user for user in get_local_resources(db= session, Resource= User).all()]
	user = get_user(session, username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
	if not user:
		raise exception
	for attr in to_check: # Maybe put this in another function
		attr_check = [getattr(user_check, attr) for user_check in users]
		if getattr(new_data, attr) != getattr(user, attr) and getattr(new_data, attr) in attr_check: 
			raise HTTPException(
				status_code = HTTP_409_CONFLICT,
				detail = attr + " with value '" + getattr(user, attr) + "' already exists"
			)
	return add_local_resource(db= session, Resource= User, user_input= new_data, r_id=user.id)

@app.delete("/{username}", response_model=UserData, dependencies=[Depends(AuthUser(3))])
async def remove_user(username: str, current_user: User = Depends(get_current_user), session= Depends(get_db)):
	user = get_user(session, username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
	return delete_local_resource(db= session, Resource= User, instance= user)

@app.delete("/{username}/connections", response_model=List[ConnectionData], dependencies=[Depends(AuthUser(3))])
async def remove_user_connections(username: str, conn_ids: List[int], current_user: User = Depends(get_current_user), session= Depends(get_db)):
	user = get_user(session, username, HTTP_404_NOT_FOUND, err_msg = "User '" + username + "' not found")
	to_delete = []
	for conn_id in conn_ids:
		connection  = get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
		conn_exists = [connection for connection in user.connections if connection.id == conn_id]
		if len(conn_exists) > 0:
			to_delete.append(conn_exists[0])
			user.connections.remove(conn_exists[0])
	session.commit()
	return to_delete

