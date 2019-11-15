from sqlalchemy.orm import Session
from pydantic import BaseModel

from daqbrokerServer.storage.base import Base

#Getting local resources, this should work for anything, as long as it has an 'id' attribute defined as PK
def get_local_resources(db: Session, Resource: Base, r_id: int = None, key_vals: dict = {}, offset: int = 0, limit: int = -1):
	query = db.query(Resource)
	if r_id:
		return query.filter(Resource.id == r_id).first()
	else:
		for attr, val in key_vals.items():
			if hasattr(Resource, attr):
				query = query.filter(getattr(Resource, attr) == val)
		query = query.offset(offset)
		if limit > 0: 
			query = query.limit(limit) #Not sure this is over, might need to change to account for offsets, should be handleable
		return query
	return None

def add_local_resource(db: Session, Resource: Base, user_input: BaseModel, r_id = None):
	if r_id:
		data_dict = user_input.dict()
		resource = get_local_resources(db= db, Resource= Resource, r_id= r_id)
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

