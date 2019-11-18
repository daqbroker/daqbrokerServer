import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

@contextmanager
def session_open(engine, auto_commit=False):
	Session = sessionmaker(bind=engine)
	sess = Session()
	try:
		yield sess
		if auto_commit:
			sess.commit()
	except:
		sess.rollback()
		raise
	finally:
		sess.close()

