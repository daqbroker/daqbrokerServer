from pydantic import BaseModel, validator

class Token(BaseModel):
	access_token: str
	token_type: str

class TokenData(BaseModel):
	username: str = None

