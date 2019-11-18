import base64
import os

from pathlib import Path
#from sqlitedict import SqliteDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from daqbrokerServer.web.utils import hash_password
from daqbrokerServer.storage.local_schema import Base, User, Connection, db_folder
from daqbrokerServer.storage.contextual_session import session_open

###### THIS CREATES THE LOCAL STRUCTURE NECESSARY TO HOLD LOCAL DATABASES #######
if not os.path.isdir(db_folder):
	os.mkdir(db_folder)

# Initialise the local settings database
local_url = "sqlite+pysqlite:///" + str(db_folder / "settings.sqlite")
local_engine = create_engine(local_url)

#################################################################################

# This should create the mappings necessary on the local database
Base.metadata.reflect(local_engine, extend_existing= True, autoload_replace= False)
Base.metadata.create_all(local_engine, checkfirst= True)

#This starts a session - probably not ideal, should consider using scoped session
LocalSession = scoped_session(sessionmaker(bind=local_engine))
Session = sessionmaker(bind=local_engine)
session = Session()


######## THIS IS VERY DANGEROUS - IT SHOULD BE A PROMPT CREATED WHEN INSTALLING THE LIBRARY
query = session.query(User).filter(User.id == 0)
if not query.count() > 0:
	pwd = "admin"
	password = hash_password(pwd)

	user = User(id= 0, type= 3, email= "mail", username= "admin", password= password)
##########################################################################################

##### THIS SHOULD LOOK FOR RECORDS OF LOCAL DATABASE, CREATES IF IT DOES NOT EXIST #######
query2 = session.query(Connection).filter(Connection.id == 0)
if not query2.count() > 0:

	connection = Connection(id= 0, type= "sqlite+pysqlite", hostname= "local", username= "admin", password= base64.b64encode(b"admin"), port=0)

##########################################################################################

#Actually adding the objects - if one does not exist the other will most likely not exist too
if (not query.count() > 0) or (not query2.count() > 0):
	connection.users.append(user)
	session.add(user)
	session.add(connection)
	session.commit()

