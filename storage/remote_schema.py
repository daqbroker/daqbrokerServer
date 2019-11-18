from sqlalchemy import Table, Column, Integer, String, Enum, LargeBinary, BigInteger, ForeignKey, create_engine, exc, inspect, orm, create_engine, event

from daqbrokerServer.storage.base import RemoteBase

class Settings(RemoteBase):
	__tablename__ = "settings"

	time = Column(BigInteger, primary_key=True)
	max_conns = Column(Integer)


