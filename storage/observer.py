from pydantic import BaseModel

from typing import List, Dict

class UpdateData(BaseModel):
	type  : str
	table : str
	key  : str
	value : Dict = {}

class Observer:
	def update(self, data: UpdateData):
		pass

class Subject:

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._observers = []

	def add_observer(self, observer):
		self._observers.append(observer)

	def rmv_observer(self, observer):
		self._observers.remove(observer)

	async def notify(self, data: UpdateData):
		for observer in self._observers:
			await observer.update(data)