from typing import List
from pydantic import BaseModel, validator

from daqbrokerServer.web.utils import hash_password

class User(BaseModel):
	username: str = None
	email: str = None
	type: int = None

	class Config:
		orm_mode = True

	@validator('type')
	def user_type_validator(cls, v):
		if v and v < 0 or v > 3:
			raise ValueError('User type field be between 0 and 3')
		return v

	@validator('username')
	def username_validator(cls, v):
		if v == "":
			raise ValueError('Username field must not be empty')
		return v

class UserInput(User):
	password: str = None

	@validator('password')
	def passwords_validator(cls, v):
		if v == "":
			raise ValueError('Password field must not be empty')
		return hash_password(v)