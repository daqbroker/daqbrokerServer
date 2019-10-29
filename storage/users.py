from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_422_UNPROCESSABLE_ENTITY

from daqbroker.storage.resource import Resource
from daqbroker.storage.instruments import Instrument

#The user resource class
class User(Resource):
	username : str
	password : str = None
	email    : str = None
	type : int = None

	def __init__(self, db, username: str, **kwargs):
		super().__init__(db, "username", username, **kwargs)

	def test_security(self, level = 0):
		self.get()
		if self.type < level:
			raise HTTPException(
				status_code=HTTP_401_UNAUTHORIZED,
				detail="You do not have permission to access this resource",
				headers={"WWW-Authenticate": "Bearer"},
			)

	def to_client(self):
		to_send = dict(self)
		del to_send["password"]
		return to_send

