from sqlalchemy.orm import Session
from pydantic import BaseModel

from daqbroker.storage.base import Base

#Getting local resources, this should work for anything, as long as it has an 'id' attribute defined as PK
def get_local_resource(db: Session, Resource: Base, r_id: int):
	return db.query(Resource).filter(Resource.id == r_id).first()

def get_local_resources(db: Session, Resource: Base, skip: int = 0, limit: int = 100):
	return db.query(Resource).offset(skip).limit(limit).all()

def get_local_by_attr(db: Session, Resource: Base, attr_name: str, attr_val):
	if hasattr(Resource, attr_name):

		return db.query(Resource).filter(getattr(Resource, attr_name) == attr_val).first()
	return None

def add_local_resource(db: Session, Resource: Base, user_input: BaseModel, r_id = None):
	if r_id:
		data_dict = user_input.dict()
		resource = get_local_resource(db= db, Resource= Resource, r_id= r_id)
		for attr, val in data_dict.items():
			if not val == None:
				setattr(resource, attr, val)
	else:
		resource = Resource(**user_input.dict())
		db.add(resource)
	db.commit()
	#db.refresh(resource)
	return resource

def delete_local_resource(db: Session, Resource: Base, instance: Base):
	db.delete(instance)
	db.commit()
	return instance

