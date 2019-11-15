import base64
import enum

from sqlalchemy import Column, Integer, String, Enum, LargeBinary, create_engine, exc, inspect
from sqlalchemy.schema import UniqueConstraint

from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import HTTPException

from daqbrokerServer.storage.base import Base

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	type = Column(Integer)
	email = Column(String, unique=True)
	username = Column(String, unique=True)
	password = Column(String)

	def test_security(self, level = 0):
		if self.type < level:
			raise HTTPException(
				status_code=HTTP_401_UNAUTHORIZED,
				detail="You do not have permission to access this resource",
				headers={"WWW-Authenticate": "Bearer"},
			)

class Connection(Base):
	__tablename__ = "connections"

	id = Column(Integer, primary_key=True)
	type = Column(String) # Maybe eventually separate the type of database with the engine used
	hostname = Column(String)
	port = Column(Integer)
	username = Column(String)
	password = Column(LargeBinary)
	__table_args__ = (UniqueConstraint("type", "hostname", "port", "username", "password", name="_connection_details"),)

	def make_url(self):
		decoded_pw = base64.b64decode(self.password).decode()
		return self.type + "://" + self.username + ":" + decoded_pw + "@" + self.hostname + ":" + str(self.port) if not "sqlite" in self.type else True

	def test(self): #SQLite test should be reviewed at a later point
		if "sqlite" in self.type:
			return (False, "Local SQLite database settings cannot be changed")
		try:
			engine = create_engine(self.make_url())
			conn = engine.connect()
			conn.close()
			return (True, "")
		except exc.OperationalError as e: # see https://docs.sqlalchemy.org/en/13/errors.html#operationalerror this is a driver error
			return (False, str(e))

	def dict(self): #Using inspector object - see https://docs.sqlalchemy.org/en/13/core/inspection.html
		return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

#TODO : Must make a many-to-many relationship between User and Connection objects to handle user access to different databases (admin-only)

