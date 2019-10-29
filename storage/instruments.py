from typing import Set, List
from pydantic import BaseModel

from daqbroker.storage.resource import Resource

class LogEntry(BaseModel):
	date: int
	author: str
	entry: str

class Instrument(Resource):
	name: str
	inst_type: int
	active: bool
	description: str = None
	owner: str
	log: Set[LogEntry]
	sources: Set[str]

	def __init__(self, db, namr: str, **kwargs):
		super().__init__(db, "name", name, **kwargs)
