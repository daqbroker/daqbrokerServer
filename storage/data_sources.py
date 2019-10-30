from typing import Set, List
from pydantic import BaseModel

from daqbrokerServer.storage.resource import Resource

class ExtraInfo(BaseModel):


class DataChannel(BaseModel):
	name : str
	val_type : int
	chn_type : int
	active : bool
	units : str = None
	description : str = None
	file_order : int
	order: int

class DataSource(Resource):
	name : str
	node : str
	data_chanels : List[DataChannel]

	def __init__(self, db, namr: str, **kwargs):
		super().__init__(db, "name", name, **kwargs)