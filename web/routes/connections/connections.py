from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_503_SERVICE_UNAVAILABLE

from daqbrokerServer.web.routes.utils import get_current_user

from daqbrokerServer.storage import session
from daqbrokerServer.storage.local_settings import Connection, User
from daqbrokerServer.web.classes.connection import Connection as ConnectionData, ConnectionInput
from daqbrokerServer.web.classes.user import User as UserData
from daqbrokerServer.storage.utils import get_local_resources, add_local_resource, delete_local_resource
from daqbrokerServer.web.routes.utils import get_connection, get_user

app = APIRouter()

@app.get("/", response_model=List[ConnectionData])
async def get_connections(current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	return [connection for connection in get_local_resources(db= session, Resource= Connection).all()]


@app.get("/{conn_id}", response_model=ConnectionData)
async def get_single_connection(conn_id: int, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	connection = get_connection(conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	return connection

@app.get("/{conn_id}/users", response_model=List[UserData])
async def get_connection_users(conn_id: int, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	connection = get_connection(conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	return [user for user in connection.users]

@app.post("/", response_model=ConnectionData)
async def add_connection(new_conn: ConnectionInput, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	exception = HTTPException(
		status_code=HTTP_409_CONFLICT,
		detail="This connection already exists"
	)
	#Must test connection here
	key_vals = {attr: getattr(new_conn, attr)  for attr in ["hostname", "port", "type"]}
	connection = get_local_resources(db= session, Resource= Connection, key_vals=key_vals).first()
	if connection:
		raise exception
	new_connection = Connection(**new_conn.dict())
	conn_test = new_connection.test()
	if conn_test[0]:
		added_conn = add_local_resource(db= session, Resource= Connection, user_input= new_conn)
		#Adding relationship parameters here - should change add_local_resource to include relationships
		added_conn.users.append(current_user)
		session.commit()
		return added_conn
	else:
		exception.status_code = HTTP_503_SERVICE_UNAVAILABLE
		exception.detail = conn_test[1]
		raise exception

@app.post("/{conn_id}/users", response_model=List[UserData])
async def get_connection_users(conn_id: int, usernames: List[str], current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	connection = get_connection(conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	for username in usernames:
		user = get_user(username, HTTP_404_NOT_FOUND, err_msg="User '" + username + "' not found")
		user_exists = [user for user in connection.users if user.username == username]
		if len(user_exists) < 1: #Should I instead raise an exception here?
			connection.users.append(user)
		#raise HTTPException(
		#	status_code=HTTP_409_CONFLICT,
		#	detail="Username '" + username + "' already assigned to this connection (id='" + str(conn_id) + "')"
		#)
	session.commit()
	return [user for user in connection.users]

@app.put("/{conn_id}", response_model=ConnectionData)
async def change_connection(conn_id: int, new_data : ConnectionInput, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	connection = get_connection(conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	connection_dict = connection.dict()
	exception = HTTPException(
		status_code=HTTP_409_CONFLICT,
		detail="Attempting to change to already existing connection"
	)
	if not connection:
		raise exception
	for attr, val in new_data.dict().items():
		if val:
			connection_dict[attr] = val
	new_connection = Connection(**connection_dict)
	key_vals = {attr: getattr(new_connection, attr) for attr in ["hostname", "port", "type"]}
	new_connection_query = get_local_resources(db= session, Resource= Connection, key_vals=key_vals).first()
	if new_connection_query:
		raise exception
	new_connection_test = new_connection.test()
	if not new_connection_test[0]:
		exception.status_code = HTTP_503_SERVICE_UNAVAILABLE
		exception.detail = new_connection_test[1]
		raise exception
	return add_local_resource(db= session, Resource= Connection, user_input= new_data, r_id=connection.id)

@app.delete("/{conn_id}", response_model=ConnectionData)
async def remove_connection(conn_id: int, current_user: Connection = Depends(get_current_user)):
	current_user.test_security(level=3)
	connection = get_connection(conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	return delete_local_resource(db= session, Resource= Connection, instance= connection)

@app.delete("/{conn_id}/users", response_model=List[UserData])
async def get_connection_users(conn_id: int, usernames: List[str], current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	connection = get_connection(conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	to_delete = []
	for username in usernames:
		user = get_user(username, HTTP_404_NOT_FOUND, err_msg="User '" + username + "' not found")
		user_exists = [user for user in connection.users if user.username == username]
		# Should consider raising an exception here if the user is not found
		if len(user_exists) > 0:
			connection.users.remove(user)
			to_delete.append(user)
	session.commit()
	return to_delete

