from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY

from daqbroker.web.routes.utils import get_current_user, make_url, test_connection

from daqbroker.storage import session
from daqbroker.storage.local_settings import Connection, User
from daqbroker.web.classes import Connection as ConnectionData
from daqbroker.web.classes import ConnectionInput
from daqbroker.storage.utils import get_local_resource, get_local_by_attr, get_local_resources, add_local_resource, delete_local_resource

app = APIRouter()

@app.get("/", response_model=List[ConnectionData])
async def get_users(current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	return [connection for connection in get_local_resources(db= session, Resource= Connection)]

#The way of making actions over specific connections must be well handled, probably over connection.id

@app.get("/{conn_id}", response_model=ConnectionData)
async def get_users(conn_id: int, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=2)
	connection = get_local_resource(db= session, Resource= Connection, r_id= conn_id)
	if not connection:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
			detail="Connection not found",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return connection

@app.post("/", response_model=ConnectionData)
async def add_user(new_conn: ConnectionInput, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	#Must test connection here
	return add_local_resource(db= session, Resource= Connection, user_input= new_conn)

@app.put("/{conn_id}", response_model=ConnectionData)
async def change_user(conn_id: int, new_data : ConnectionInput, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	connection = get_local_resource(db= session, Resource= Connection, r_id= conn_id)
	exception = HTTPException(
		status_code=HTTP_404_NOT_FOUND,
		detail="Connection not found",
		headers={"WWW-Authenticate": "Bearer"},
	)
	if not connection:
		raise exception
	return add_local_resource(db= session, Resource= User, user_input= new_data, r_id=user.id)
#	users = [user for user in get_local_resources(db= session, Resource= User)]
#	user = get_local_by_attr(db= session, Resource= User, attr_name= "username", attr_val= username)
#	exception = HTTPException(
#		status_code=HTTP_404_NOT_FOUND,
#		detail="User '" + username + "' not found",
#		headers={"WWW-Authenticate": "Bearer"},
#	)
#	if not user:
#		raise exception
#	for attr in to_check:
#		attr_check = [getattr(user_check, attr) for user_check in users]
#		if getattr(new_data, attr) != getattr(user, attr) and getattr(new_data, attr) in attr_check:
#			status_code=HTTP_409_CONFLICT,
#			exception.detail = attr + " with value '" + getattr(user, attr) + "' already exists"
#			raise exception
#	return add_local_resource(db= session, Resource= User, user_input= new_data, r_id=user.id)

#@app.delete("/{username}", response_model=ConnectionData)
#async def remove_user(username: str, current_user: User = Depends(get_current_user)):
#	current_user.test_security(level=2)
#	user = get_local_by_attr(db= session, Resource= User, attr_name= "username", attr_val= username)
#	if not user:
#		raise HTTPException(
#			status_code=HTTP_404_NOT_FOUND,
#			detail="User '" + username + "' not found",
#			headers={"WWW-Authenticate": "Bearer"},
#		)
#	return delete_local_resource(db= session, Resource= User, instance= user)

