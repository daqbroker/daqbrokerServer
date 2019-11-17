import base64

from enum import Enum
from typing import List
from pydantic import BaseModel, validator


class ConnectionTypes(str, Enum):
	sqlite = "sqlite+pysqlite" # SQLite is not a remote database, there will only be one entry
	mysql = "mysql"

class ConnBase(BaseModel):
	hostname: str = None
	username: str = None
	port: int = None
	type: ConnectionTypes = None

class Connection(ConnBase):
	id: int = None

	class Config:
		orm_mode = True

class ConnectionInput(ConnBase):
	password: str = None

	@validator('password')
	def passwords_validator(cls, v):
		if v == "":
			raise ValueError('Password field must not be empty')
		return base64.b64encode(v.encode("utf-8"))

