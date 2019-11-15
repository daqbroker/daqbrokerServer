from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_503_SERVICE_UNAVAILABLE

from daqbrokerServer.web.routes.utils import get_current_user, make_url

from daqbrokerServer.storage import session
from daqbrokerServer.storage.local_settings import Connection, User
from daqbrokerServer.web.classes import Connection as ConnectionData
from daqbrokerServer.web.classes import ConnectionInput
from daqbrokerServer.storage.utils import get_local_resources, add_local_resource, delete_local_resource

app = APIRouter()

@app.get("/", response_model=List[ConnectionData])
async def get_connections(current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	return [connection for connection in get_local_resources(db= session, Resource= Connection).all()]

#The way of making actions over specific connections must be well handled, probably over connection.id

@app.get("/{conn_id}", response_model=ConnectionData)
async def get_connection(conn_id: int, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	connection = get_local_resources(db= session, Resource= Connection, r_id= conn_id)
	if not connection:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
			detail="Connection not found",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return connection

@app.post("/", response_model=ConnectionData)
async def add_connection(new_conn: ConnectionInput, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	exception = HTTPException(
		status_code=HTTP_409_CONFLICT,
		detail="This connection already exists",
		headers={"WWW-Authenticate": "Bearer"},
	)
	#Must test connection here
	key_vals = {attr: getattr(new_conn, attr)  for attr in ["hostname", "port", "type"]}
	connection = get_local_resources(db= session, Resource= Connection, key_vals=key_vals).first()
	if connection:
		raise exception
	new_connection = Connection(**new_conn.dict())
	conn_test = new_connection.test()
	if conn_test[0]:
		return add_local_resource(db= session, Resource= Connection, user_input= new_conn)
	else:
		exception.status_code = HTTP_503_SERVICE_UNAVAILABLE
		exception.detail = conn_test[1]
		raise exception

@app.put("/{conn_id}", response_model=ConnectionData)
async def change_connection(conn_id: int, new_data : ConnectionInput, current_user: User = Depends(get_current_user)):
	current_user.test_security(level=3)
	connection = get_local_resources(db= session, Resource= Connection, r_id= conn_id)
	connection_dict = connection.dict()
	exception = HTTPException(
		status_code=HTTP_404_NOT_FOUND,
		detail="Connection not found",
		headers={"WWW-Authenticate": "Bearer"},
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
		exception.status_code = HTTP_409_CONFLICT
		exception.detail = "Attempting to change to already existing connection"
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
	connection = get_local_resources(db= session, Resource= Connection, r_id= conn_id)
	if not connection:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
			detail="User '" + username + "' not found",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return delete_local_resource(db= session, Resource= Connection, instance= connection)

