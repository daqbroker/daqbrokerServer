import os
import pytest
import time

from pathlib import Path

from starlette.testclient import TestClient

from daqbrokerServer.web import WebServer

empty_modules = [
	"test_connections"
]

@pytest.fixture(scope="module")
def client(request):
	module_name = request.module.__name__
	db_path = Path(__file__).parent / "settings.sqlite"
	empty = False
	if any(name in module_name for name in empty_modules): empty = True
	test_server = WebServer( db_folder=Path(__file__).parent, empty_connections=empty )
	with TestClient(test_server.app) as client:
		yield client
	os.remove(Path(__file__).parent / "settings.sqlite")
	time.sleep(1)

@pytest.fixture
def token(client):
	response = client.post(
		"/api/auth/token",
		data= {"username": "admin", "password": "admin"}, #I should outside create a random user and password
	)
	if response.status_code == 200:
		return response.json()
	else:
		return None

