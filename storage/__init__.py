import base64
import os
import threading

from pathlib import Path
#from sqlitedict import SqliteDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from daqbrokerServer.web.utils import hash_password
from daqbrokerServer.storage.server_schema import ServerBase, User, Connection
from daqbrokerServer.storage.contextual_session import session_open

# ###### THIS CREATES THE LOCAL STRUCTURE NECESSARY TO HOLD LOCAL DATABASES #######
# if not os.path.isdir(db_folder):
# 	os.mkdir(db_folder)

# # Initialise the local settings database
# local_url = "sqlite+pysqlite:///" + str(db_folder / "settings.sqlite")
# local_engine = create_engine(local_url)

# #################################################################################

# # This should create the mappings necessary on the local database
# Base.metadata.reflect(local_engine, extend_existing= True, autoload_replace= False)
# Base.metadata.create_all(local_engine, checkfirst= True)

# #This starts a session - probably not ideal, should consider using scoped session
# #LocalSession = scoped_session(sessionmaker(bind=local_engine))
# Session = sessionmaker(bind=local_engine)
# session = Session()

# Experimenting a class that will handle the folder definition of the session for the server class
class LocalSession:
	def __init__(self, db_folder= None, empty_connections= False):


		self.db_folder = None if db_folder == None else Path(db_folder)
		self.url = "sqlite+pysqlite:///" + str( ( self.db_folder if self.db_folder else Path(__file__).parent / "databases" )  / "settings.sqlite")
		self.engine = create_engine(self.url)
		self.session = scoped_session(sessionmaker(bind=self.engine))

		ServerBase.metadata.reflect(self.engine, extend_existing= True, autoload_replace= False)
		ServerBase.metadata.create_all(self.engine, checkfirst= True)

		Connection.set_db_folder(self.db_folder)

		self.setup(empty_connections)

	def setup(self, empty_connections= False):
		test_session = self.session()

		######## THIS IS VERY DANGEROUS - IT SHOULD BE A PROMPT CREATED WHEN INSTALLING THE LIBRARY
		query = test_session.query(User).filter(User.id == 0)
		if not query.count() > 0:
			pwd = "admin"
			password = hash_password(pwd)

			user = User(id= 0, type= 3, email= "mail", username= "admin", password= password)
			if not query.count() > 0:
				test_session.add(user)
		##########################################################################################

		if not empty_connections:
			##### THIS SHOULD LOOK FOR RECORDS OF LOCAL DATABASE, CREATES IF IT DOES NOT EXIST #######
			query2 = test_session.query(Connection).filter(Connection.id == 0)
			if not query2.count() > 0:

				connection = Connection(id= 0, type= "sqlite+pysqlite", hostname= "local", username= "admin", password= base64.b64encode(b"admin"), port=0)
				if not query2.count() > 0:
					test_session.add(connection)

		##########################################################################################

		#Actually adding the object(s)
		test_session.commit()

	def teardown(self):
		self.engine.dispose()

# ######## THIS IS VERY DANGEROUS - IT SHOULD BE A PROMPT CREATED WHEN INSTALLING THE LIBRARY
# query = session.query(User).filter(User.id == 0)
# if not query.count() > 0:
# 	pwd = "admin"
# 	password = hash_password(pwd)

# 	user = User(id= 0, type= 3, email= "mail", username= "admin", password= password)
# ##########################################################################################

# ##### THIS SHOULD LOOK FOR RECORDS OF LOCAL DATABASE, CREATES IF IT DOES NOT EXIST #######
# query2 = session.query(Connection).filter(Connection.id == 0)
# if not query2.count() > 0:

# 	connection = Connection(id= 0, type= "sqlite+pysqlite", hostname= "local", username= "admin", password= base64.b64encode(b"admin"), port=0)

# ##########################################################################################

# #Actually adding the objects - if one does not exist the other will most likely not exist too
# if (not query.count() > 0) or (not query2.count() > 0):
# 	connection.users.append(user)
# 	session.add(user)
# 	session.add(connection)
# 	session.commit()

