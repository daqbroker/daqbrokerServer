import pytest

#Tests for the '/api/users' routes

users_to_test = [
	{
		"username": "user1",
		"email": "fancymail1@server.com",
		"type": 0,
		"password": "pass1"
	},
	{
		"username": "user2",
		"email": "fancymail2@server.com",
		"type": 1,
		"password": "pass2"
	},
	{
		"username": "user3",
		"email": "fancymail3@server.com",
		"type": 2,
		"password": "pass3"
	},
	{
		"username": "user4",
		"email": "fancymail4@server.com",
		"type": 3,
		"password": "pass4"
	},
]

edit_tests = [
	{
		"type": 2,
	},
	{
		"password": "funkypass",
		"type": 2,
	},
	{
		"email": "emailsareimportant@emailserver.com",
		"password": "funkypass",
		"type": 2,
	},
	{
		"username": "usernotexists", 
		"email": "emailsareimportant2@emailserver.com",
		"password": "funkypass",
		"type": 2,
	}
]

def test_users_get(token, client):
	assert token #Must test access token to ensure proper 

	response = client.get(
		"/api/users/",
		headers= {"Authorization":	"Bearer "+ token["access_token"]}
	)

	assert response.status_code == 200
	assert type(response.json()) == list

#Maybe I should make a test for bad user input at some point
@pytest.mark.parametrize("user", users_to_test)
def test_users_add(token, client, user):
	response = client.post(
		"/api/users/",
		headers= {"Authorization": "Bearer "+ token["access_token"]},
		json=user
	)

	response_user = {key: val for key, val in user.items() if not key == "password" }

	assert response.status_code == 200
	assert response.json() == response_user

@pytest.mark.parametrize("user_edits, user", [(edit, users_to_test[idx]) for idx,edit in enumerate(edit_tests) ])
def test_users_edit(token, client, user_edits, user):
	url = "/api/users/" + user["username"]
	response = client.put(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]},
		json=user_edits
	)

	response_user = {}
	original_index = next((index for (index, d) in enumerate(users_to_test) if d["username"] == user["username"]), None)
	for key, val in user.items():
		if not key == "password":
			response_user[key] = val
			if key in user_edits:
				response_user[key] = user_edits[key]
		if key in user_edits: # This will alter the original values of users_to_test
			users_to_test[original_index][key] = user_edits[key]

	assert response.status_code == 200
	assert response.json() == response_user

@pytest.mark.parametrize("user", users_to_test)
def test_user_get(token, client, user):
	url = "/api/users/" + user["username"]
	response = client.get(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]},
		json=user
	)

	response_user = {key: val for key, val in user.items() if not key == "password" }

	assert response.status_code == 200
	assert response.json() == response_user

@pytest.mark.parametrize("user", (users_to_test[0], ))
def test_user_connections_get(token, client, user):
	url = "/api/users/" + user["username"] + "/connections"
	response = client.get(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]},
	)

	assert response.status_code == 200
	assert response.json() == [] # This should be the case because the user is new, should not be the case for all users
	# assert type(response.json()) == list # This is an alternative to the above that should work for all users

@pytest.mark.parametrize("user", (users_to_test[0], ))
def test_user_connections_set(token, client, user):
	url = "/api/users/" + user["username"] + "/connections"
	response = client.post(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]},
		json=[0] # Assigning to this user the use of the default local connection that should exist for all DAQBroker servers
	)

	expected = [
		{
			"hostname": "local",
			"username": "admin",
			"port": 0,
			"type": "sqlite+pysqlite",
			"id": 0,
			"connectable": True
		}
	]

	assert response.status_code == 200
	assert response.json() == expected

@pytest.mark.parametrize("user", (users_to_test[0], ))
def test_user_connections_remove(token, client, user):
	url = "/api/users/" + user["username"] + "/connections"
	response = client.delete(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]},
		json=[0] # Assigning to this user the use of the default local connection that shouldm exists for all DAQBroker servers
	)

	expected = [
		{
			"hostname": "local",
			"username": "admin",
			"port": 0,
			"type": "sqlite+pysqlite",
			"id": 0,
			"connectable": True
		}
	]

	assert response.status_code == 200
	assert response.json() == expected # This endpoint returns a LIST OF THE REMOVED CONNECTIONS
	# maybe consider refactoring to show the list of the users' current connections?

@pytest.mark.parametrize("user", users_to_test)
def test_users_remove(token, client, user):
	url = "/api/users/" + user["username"]
	response = client.delete(
		url,
		headers= {"Authorization": "Bearer "+ token["access_token"]},
	)

	response_user = {key: val for key, val in user.items() if not key == "password" }

	assert response.status_code == 200
	assert response.json() == response_user

