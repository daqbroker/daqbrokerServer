import base64

from pathlib import Path
#from sqlitedict import SqliteDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from daqbrokerServer.web.utils import hash_password
from daqbrokerServer.storage.local_settings import Base, User, Connection

local_url = "sqlite+pysqlite:///" + str(Path(__file__).parent / "storage_local.sqlite")
local_engine = create_engine(local_url)

Base.metadata.reflect(local_engine, extend_existing= True, autoload_replace= False)
Base.metadata.create_all(local_engine, checkfirst= True)

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

