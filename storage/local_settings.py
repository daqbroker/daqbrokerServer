import enum

from sqlalchemy import Column, Integer, String, Enum
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
	password = Column(String)
	__table_args__ = (UniqueConstraint("type", "hostname", "port", "username", "password", name="_connection_details"),)
