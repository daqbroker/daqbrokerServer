def test_auth(client):
	response = client.post(
		"/api/auth/token",
		data={"username": "admin", "password": "admin"}, #I should outside create a random user and password
	)
	assert response.status_code == 200
	assert all(key in response.json() for key in ["access_token", "token_type"])

