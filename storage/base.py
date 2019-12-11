from sqlalchemy.ext.declarative import declarative_base

# Base used on the local settings database
ServerBase = declarative_base()

# Base used to describe a daqbroker database
DaqbrokerBase = declarative_base()

def get_base():
	return Base