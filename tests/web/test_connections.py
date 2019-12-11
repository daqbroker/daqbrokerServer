"""
Tests the endpoints that handle connetion CRUD mechanics on a DAQBroker server's local database

WARNING: These tests make use of the pytest.skip method to test whether a specific RDBMS method is running on your machine
"""

import pytest
from importlib import import_module

conns_to_test= [
	{
		"hostname": "localhost",
		"username": "root",
		"port": 3306,
		"type": "mysql",
		"password": "abcd"
	},
	{
		"hostname": "localhost",
		"username": "admin",
		"port": 0,
		"type": "sqlite+pysqlite",
		"password": "admin"
	},
	{
		"hostname": "localhost",
		"username": "root",
		"port": 0,
		"type": "postgres",
		"password": "abcd"
	}
]

conn_edits = [ # Gotta put some connection edit dicts here eventually
]

conn_campaigns = [
	"campaign_1",
	"campaign_2",
	"campaign_3"
]

test_campaigns = []
test_users = []

conn_reference = {
	"mysql": {
		"package": "MySQLdb",
		"error": "something.something"
	},
	"sqlite+pysqlite": {
		"package": "sqlite3",
		"error": "something.something"
	},
	"postgres": { #Must change here
		"package": "postgres", #Must change here
		"error": "something.something"
	}
}

def skip_by_connection(connection):
	if not "id" in connection:
		pytest.skip("`test_connections_add` failed for this object or server is not prepared for `" + connection["type"] + "` databases")
		pass

def test_connections_get(token, client):
	assert token #Must test access token to ensure proper 

	response = client.get(
		"/api/connections/",
		headers= {"Authorization":	"Bearer "+ token["access_token"]}
	)

	assert response.status_code == 200
	assert type(response.json()) == list

@pytest.mark.parametrize("connection", conns_to_test)
def test_connections_add(token, client, connection):
	try:
		import_module( conn_reference[connection["type"]]["package"] )
		response = client.post(
			"/api/connections/",
			headers= {"Authorization": "Bearer "+ token["access_token"]},
			json=connection
		)

		assert response.status_code == 200

		response_user = {key: val for key, val in connection.items() if not key == "password" }
		response_api = response.json()

		original_index = next((index for (index, d) in enumerate(conns_to_test) if d["type"] == connection["type"]), None)

		# asserts here don't care for what comes extra from the api, specifically `connectable` and `id` attributes
		# should it? I am not sure, I just want to make sure what comes out of the api is the same as what went in
		# Replace original with these, this way I know the IDs for deletion
		for key, val in response_api.items():
			if key in response_user:
				assert response_user[key] == val
			else:
				conns_to_test[original_index][key] = val # CONSIDERATION - REMOVE WHEN REMOVING THE SKIP FOR THE `test_connections_edit` METHOD

	except ModuleNotFoundError as error:
		pytest.skip("Machine not setup for postgres access")

@pytest.mark.skip(reason="Very complex to test, must ensure many connections in same machine for single database")
@pytest.mark.parametrize("connection", conn_edits)
def test_connections_edit(token, client, connection):
	pass

@pytest.mark.parametrize("connection", conns_to_test)
def test_connection_get(token, client, connection):
	skip_by_connection(connection)
	url = "/api/connections/" + str(connection["id"])
	response = client.get(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]}
	)

	assert response.status_code == 200

	response_user = {key: val for key, val in connection.items() if not key == "password" }
	response_api = response.json()

	for key, val in response_api.items():
		if key in response_user:
			assert response_user[key] == val

@pytest.mark.parametrize("connection", conns_to_test)
def test_connection_campaigns_get(token, client, connection):
	skip_by_connection(connection)


	url = "/api/connections/" + str(connection["id"]) + "/campaigns"
	response = client.get(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]}
	)

	assert response.status_code == 200
	assert type(response.json()) == list

	if len(test_campaigns) == 0:
		for name in response.json():
			test_campaigns.append(name)

@pytest.mark.parametrize("connection", conns_to_test)
def test_connection_campaigns_add(token, client, connection):
	skip_by_connection(connection)

	for name in conn_campaigns:
		url = "/api/connections/" + str(connection["id"]) + "/campaigns?campaign=" + name
		response = client.post(
			url,
			headers= {"Authorization": "Bearer "+ token["access_token"]}
		)

		assert response.status_code == 200

		test_campaigns.append(name)

		assert all(name in test_campaigns for name in response.json()) == True

@pytest.mark.parametrize("connection", conns_to_test)
def test_connection_campaigns_remove(token, client, connection):
	skip_by_connection(connection)

	for name in conn_campaigns:
		url = "/api/connections/" + str(connection["id"]) + "/campaigns?campaign=" + name
		response = client.delete(
			url,
			headers= {"Authorization": "Bearer "+ token["access_token"]}
		)

		assert response.status_code == 200

		test_campaigns.remove(name)

		assert all(name in test_campaigns for name in response.json()) == True

@pytest.mark.parametrize("connection", conns_to_test)
def test_connection_users_get(token, client, connection):
	skip_by_connection(connection)

	url = "/api/connections/" + str(connection["id"]) + "/users"
	response = client.get(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]}
	)

	assert response.status_code == 200

	assert type(response.json()) == list

	if len(test_campaigns) == 0:
		for user in response.json():
			test_users.append(user)

@pytest.mark.parametrize("connection", conns_to_test)
def test_connection_users_assign(token, client, connection):
	skip_by_connection(connection)
	
	url = "/api/connections/" + str(connection["id"]) + "/users"
	response = client.post(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]},
		json= [user["username"] for user in test_users]
	)

	assert response.status_code == 200

	for user in response.json():
		if not user in test_users:
			test_users.append(user)

	assert all(user in test_users for user in response.json()) == True

@pytest.mark.parametrize("connection", conns_to_test)
def test_connection_users_remove(token, client, connection):
	skip_by_connection(connection)
	
	url = "/api/connections/" + str(connection["id"]) + "/users"
	response = client.delete(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]},
		json= [user["username"] for user in test_users]
	)

	assert response.status_code == 200

	for user in response.json():
		if user in test_users:
			test_users.remove(user)

	assert any(user in test_users for user in response.json()) == False

@pytest.mark.parametrize("connection", conns_to_test)
def test_connections_remove(token, client, connection):
	skip_by_connection(connection)
	url = "/api/connections/" + str(connection["id"])
	response = client.delete(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]},
	)

	assert response.status_code == 200

	response_user = {key: val for key, val in connection.items() if not key == "password" }
	response_api = response.json()

	# asserts here don't care for what comes extra from the api, specifically `connectable` and `id` attributes
	# should it? I am not sure, I just want to make sure what comes out of the api is the same as what went in
	for key, val in response_api.items():
		if key in response_user:
			assert response_user[key] == val

