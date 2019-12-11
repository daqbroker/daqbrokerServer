from sqlalchemy import Table, Column, Integer, String, Enum, LargeBinary, BigInteger, Text, ForeignKey, create_engine, exc, inspect, orm, create_engine, event

from daqbrokerServer.storage.base import DaqbrokerBase

class Settings(DaqbrokerBase):
	__tablename__ = "settings"

	time = Column(BigInteger, primary_key=True)
	max_conns = Column(Integer)
	#max_instruments = Column(Integer)

class Instrument(DaqbrokerBase):
	__tablename__ = "instruments"

	id = Column(Integer, primary_key=True)
	name = Column(String(50), unique=True)

	# This is a problematic column
	# This column must contain a value that UNIQUELY identifies the user
	# It is not enough to put the name of the user
	owner = Column(String(128))

	contact_email = Column(String(50))
	contact_phone = Column(String(50))
	description = Column(Text)

	# Should eventually have here a many-to-one relationship to sources

	# A funciton should exist here (__init__?) to create the tables for the instrument

