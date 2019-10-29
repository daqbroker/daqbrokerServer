from sqlalchemy.ext.declarative import declarative_base

#Declarative base?
Base = declarative_base()

def get_base():
	return Base