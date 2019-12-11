import uvicorn
import threading
from pathlib import Path
from fastapi import FastAPI
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, HTMLResponse, Response

from daqbrokerServer.web.api import api
import daqbrokerServer.web.routes.utils as utils
from daqbrokerServer.web.frontend import frontend
from daqbrokerServer.storage import LocalSession

def setup_api(**kwargs):

	main_app = FastAPI()

	#local_session = LocalSession(**kwargs)
	#local_session.setup()

	@main_app.on_event("startup")
	def open_database_connection_pools():
		utils.local_session = LocalSession(**kwargs)

	@main_app.on_event("shutdown")
	def close_database_connection_pools():
		if utils.local_session: utils.local_session.teardown()

	# @main_app.middleware("http")
	# def db_session_middleware(request: Request, call_next):
	# 	response = Response("Internal server error", status_code=500)
	# 	try:
	# 		sess = local_session.session()
	# 		request.state.local_session = sess #local_session.session
	# 		#for key,val in kwargs.items():
	# 		#	setattr(request.state, key, val)
	# 		print("MIDDLEWARE ENGAGED", threading.get_ident())
	# 		response = await call_next(request)
	# 	finally:
	# 		print("MIDDLEWARE CLOSING", threading.get_ident())
	# 		sess.close()
	# 	return response

	return main_app

class WebServer:
	def __init__(self, **kwargs):
		self.host = kwargs["host"] if "host" in kwargs else "127.0.0.1"
		self.port = kwargs["port"] if "port" in kwargs else 8001
		self.log_level = kwargs["log_level"] if "log_level" in kwargs else "info"

		app_conf_keys = ["db_folder", "empty_connections"] # Keys to send to request
		app_config = { key: val for key, val in kwargs.items() if key in app_conf_keys}

		self.app = setup_api(**app_config)

		self.config = uvicorn.Config(self.app, host= self.host, port= self.port, log_level=self.log_level, loop="asyncio")
		self.server = uvicorn.Server(self.config)

		self.app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / 'daqbrokerfrontend')), name="static")
		self.app.include_router(api, prefix="/api")

		@self.app.get("/api/.*", status_code=404, include_in_schema=False)
		def invalid_api():
			return None

		@self.app.get("/.*", include_in_schema=False)
		def root():
			return FileResponse(str(Path(__file__).parent / 'daqbrokerfrontend/index.html'))

	def serve(self):
		return self.server.serve()
		#uvicorn.run(self.app, host=self.host, port=self.port, log_level=self.log_level)

