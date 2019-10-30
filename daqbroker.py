import random
import asyncio

from sqlalchemy.orm import sessionmaker

from daqbrokerServer.web import WebServer
from daqbrokerServer.storage import local_engine

Session = sessionmaker()
Session.configure(bind=local_engine)
session = Session()

async def stupid():
	while True:
		await asyncio.sleep(1)

class DAQBrokerServer:
	def __init__(self, **kwargs):
		try:
			self.loop = asyncio.get_running_loop()
		except RuntimeError:
			self.loop = asyncio.get_event_loop()
		self.web_server = WebServer(**kwargs)

	def start(self):
		self.loop.create_task(self.web_server.serve())
		self.loop.create_task(stupid())
		self.loop.run_forever()

