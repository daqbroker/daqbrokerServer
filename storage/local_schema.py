import base64
import enum
import os
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import Table, Column, Integer, String, Enum, LargeBinary, ForeignKey, create_engine, exc, inspect, orm, create_engine, event
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql import text

from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import HTTPException

from daqbrokerServer.storage.base import Base
from daqbrokerServer.storage.remote_schema import RemoteBase

users_connections = Table(
	"users_connections",
	Base.metadata,
	Column("connection", Integer, ForeignKey("connections.id")),
	Column("user", String, ForeignKey("users.username"))
)

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	type = Column(Integer)
	email = Column(String, unique=True)
	username = Column(String, unique=True)
	password = Column(String)
	connections = orm.relationship("Connection", secondary=users_connections, back_populates="users")

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
	password = Column(LargeBinary)
	users = orm.relationship("User", secondary=users_connections, back_populates="connections")
	__table_args__ = (UniqueConstraint("type", "hostname", "port", "username", "password", name="_connection_details"),)

	db_folder = Path(__file__).parent / "databases"

	def __init__ (
		self, type: str = None, hostname: str = None, port: int = None, username: str = None, password: str = b'', users: list = [], db_folder: str = None, id: int = None
	):

		# Database things
		self.id = id
		self.type = type
		self.hostname = hostname
		self.port = port
		self.username = username
		self.password = password
		self.users = users

		# Setup the database, make connection tests, check databses, etc...
		self.setup()

	def make_url(self):
		decoded_pw = base64.b64decode(self.password).decode()
		if "sqlite" in self.type:
			self.url = self.type + ":///" + str(self.db_folder / "settings.sqlite") if not self.database else self.type + ":///" + str(self.db_folder / (self.database + ".sqlite"))
		else:
			self.url = self.type + "://" + self.username + ":" + decoded_pw + "@" + self.hostname + ":" + str(self.port)
			if self.database:
				self.url = self.url + "/" + self.database

	def make_engine(self):
		self.make_url()
		self.engine = create_engine(self.url)
		self.Session = orm.sessionmaker(bind=self.engine)
		self.inspector = inspect(self.engine)

	def get_databases(self):
		self.test()
		if self.connectable:
			if "sqlite" in self.type:
				self.databases = tuple(db_name.split(".")[0] for db_name in os.listdir(self.db_folder) if "daqbroker_" in db_name)
			else:
				self.databases = tuple(db_name for db_name in self.inspector.get_schema_names() if "daqbroker_" in db_name)
		self.campaigns = tuple("_".join(db_name.split("_")[1:]) for db_name in self.databases)

	def create_database(self, database):
		self.get_databases()
		if database not in self.databases:
			if not "sqlite" in self.type:
				with self.session() as session:
					command = text("CREATE DATABASE " + database)
					session.execute(command)
			self.database = database
			self.test() # This should update the engine & session objects
			if self.connectable:
				# This should get all the stuff and create all the stuff that needs creating
				RemoteBase.metadata.reflect(self.engine, extend_existing= True, autoload_replace= False)
				RemoteBase.metadata.create_all(self.engine, checkfirst= True)

	def remove_database(self, database):
		self.get_databases()
		if database in self.databases:
			if not "sqlite" in self.type:
				with self.session() as session:
					command = text("DROP DATABASE " + database)
					session.execute(command)
			else:
				db_path = self.db_folder / ( database + ".sqlite" )
				if db_path.is_file():
					os.remove(db_path)
				else:
					# Should there be an exception here?!
					print("COULD NOT FIND PATH FOR THIS DATABASE", db_path)

	@classmethod
	def set_db_folder(self, db_folder=None):
		self.db_folder = Path(__file__).parent / "databases" if db_folder == None else Path(db_folder)

	@contextmanager
	def session(self, **kwargs):
		try:
			sess = self.Session(**kwargs)
			yield sess
			# if auto_commit:
			# 	sess.commit()
		except:
			sess.rollback()
			raise
		finally:
			sess.close()

	def test(self): #SQLite test should be reviewed at a later point
		self.make_engine()
		if "sqlite" in self.type:
			self.connectable = True
			self.conn_error = None
		try:
			conn = self.engine.connect()
			conn.close()
			self.connectable = True
			self.conn_error = None
		except exc.OperationalError as e: # see https://docs.sqlalchemy.org/en/13/errors.html#operationalerror this is a driver error
			print("THERE WAS AN ERROR")
			self.connectable = False
			self.conn_error = str(e)

	def dict(self): #Using inspector object - see https://docs.sqlalchemy.org/en/13/core/inspection.html
		return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

	def setup(self):
		self.database = None
		self.databases = ()
		self.campaigns = ()
		self.get_databases()

class Node(Base):
	id = Column(Integer, primary_key=True)
	uuid = Column(String)
	ip = Column(String)
	port = Column(Integer)


@event.listens_for(Connection, 'load')
def on_load_connection(target, value):
	target.setup()

