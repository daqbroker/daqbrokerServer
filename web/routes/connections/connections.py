from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_503_SERVICE_UNAVAILABLE

from daqbrokerServer.web.routes.utils import AuthUser
from daqbrokerServer.storage.local_schema import Connection, User
from daqbrokerServer.web.classes.connection import Connection as ConnectionData, ConnectionInput
from daqbrokerServer.web.classes.user import User as UserData
from daqbrokerServer.storage.utils import get_local_resources, add_local_resource, delete_local_resource
from daqbrokerServer.web.routes.utils import get_connection, get_user, get_db, test_connection, add_campaign, remove_campaign

app = APIRouter()

@app.get("/", response_model=List[ConnectionData], dependencies=[Depends(AuthUser(3))])
async def get_connections(session= Depends(get_db)):
	return [connection for connection in get_local_resources(db= session, Resource= Connection).all()]


@app.get("/{conn_id}", response_model=ConnectionData, dependencies=[Depends(AuthUser(3))])
async def get_single_connection(conn_id: int, session= Depends(get_db)):
	return get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")

@app.get("/{conn_id}/users", response_model=List[UserData], dependencies=[Depends(AuthUser(3))])
async def get_connection_users(conn_id: int, session= Depends(get_db)):
	connection = get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	return [user for user in connection.users]

@app.get("/{conn_id}/campaigns", response_model=List[str], dependencies=[Depends(AuthUser(3))])
async def get_connection_users(conn_id: int, session= Depends(get_db)):
	connection = get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	return connection.campaigns

@app.post("/", response_model=ConnectionData, dependencies=[])
async def add_connection(new_conn: ConnectionInput, session= Depends(get_db), current_user: User = Depends(AuthUser(3))):
	exception = HTTPException(
		status_code=HTTP_409_CONFLICT,
		detail="This connection already exists"
	)
	#Must test connection here
	key_vals = {attr: getattr(new_conn, attr)  for attr in ["hostname", "port", "type"]}
	connection = get_local_resources(db= session, Resource= Connection, key_vals=key_vals).first()
	if connection:
		raise exception
	new_connection = Connection(**new_conn.dict()) # This object only wastes memory, should there be a way to send the object over 'add_local_resource' as 'user_input'
	test_connection(new_connection)
	added_conn = add_local_resource(db= session, Resource= Connection, user_input= new_conn)
	added_conn.setup()
	# Adding relationship parameters here - should change add_local_resource to include relationships
	added_conn.users.append(current_user) # Currrently doesn't work because there is no instance of the User class representing the logged user
	session.commit()
	return added_conn

@app.post("/{conn_id}/users", response_model=List[UserData], dependencies=[Depends(AuthUser(3))])
async def add_users_to_connection(conn_id: int, usernames: List[str], session= Depends(get_db)):
	connection = get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	for username in usernames:
		user = get_user(session, username, HTTP_404_NOT_FOUND, err_msg="User '" + username + "' not found")
		user_exists = [user for user in connection.users if user.username == username]
		if len(user_exists) < 1: #Should I instead raise an exception here?
			connection.users.append(user)
		#raise HTTPException(
		#	status_code=HTTP_409_CONFLICT,
		#	detail="Username '" + username + "' already assigned to this connection (id='" + str(conn_id) + "')"
		#)
	session.commit()
	return [user for user in connection.users]

@app.post("/{conn_id}/campaigns", response_model=List[str], dependencies=[Depends(AuthUser(3))])
async def add_campaign_to_connection(conn_id: int, campaign: str, session= Depends(get_db)):
	connection = get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	return add_campaign(connection, campaign)

@app.put("/{conn_id}", response_model=ConnectionData, dependencies=[Depends(AuthUser(3))])
async def change_connection(conn_id: int, new_data : ConnectionInput, session= Depends(get_db)):
	connection = get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
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

@app.delete("/{conn_id}", response_model=ConnectionData, dependencies=[Depends(AuthUser(3))])
async def remove_connection(conn_id: int, session= Depends(get_db)):
	connection = get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	return delete_local_resource(db= session, Resource= Connection, instance= connection)

@app.delete("/{conn_id}/users", response_model=List[UserData], dependencies=[Depends(AuthUser(3))])
async def remove_users_from_connection(conn_id: int, usernames: List[str], session= Depends(get_db)):
	connection = get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	to_delete = []
	for username in usernames:
		user = get_user(session, username, HTTP_404_NOT_FOUND, err_msg="User '" + username + "' not found")
		user_exists = [user for user in connection.users if user.username == username]
		# Should consider raising an exception here if the user is not found
		if len(user_exists) > 0:
			connection.users.remove(user)
			to_delete.append(user)
	session.commit()
	return to_delete

@app.delete("/{conn_id}/campaigns", response_model=List[str], dependencies=[Depends(AuthUser(3))])
async def remove_campaign_from_connection(conn_id: int, campaign: str, session= Depends(get_db)):
	connection = get_connection(session, conn_id, HTTP_404_NOT_FOUND, err_msg="Connection with id='" + str(conn_id) + "' not found")
	return remove_campaign(connection, campaign)