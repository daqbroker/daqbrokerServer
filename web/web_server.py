import uvicorn
from pathlib import Path
from fastapi import FastAPI
from starlette.responses import FileResponse, HTMLResponse
from starlette.staticfiles import StaticFiles

from daqbrokerServer.web.api import api
from daqbrokerServer.web.frontend import frontend

main_app = FastAPI()

class WebServer:
	def __init__(self, **kwargs):
		self.host = kwargs["host"] if "host" in kwargs else "127.0.0.1"
		self.port = kwargs["port"] if "port" in kwargs else 8001
		self.log_level = kwargs["log_level"] if "log_level" in kwargs else "info"
		self.app = main_app
		self.config = uvicorn.Config(self.app, host= self.host, port= self.port, log_level=self.log_level, loop="asyncio")
		self.server = uvicorn.Server(self.config)

		self.app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / 'frontend/dist')), name="static")
		self.app.include_router(api, prefix="/api")

		@self.app.get("/api/.*", status_code=404, include_in_schema=False)
		def invalid_api():
			return None

		@self.app.get("/.*", include_in_schema=False)
		def root():
			return FileResponse(str(Path(__file__).parent / 'frontend/dist/index.html'))

	def serve(self):
		return self.server.serve()
		#uvicorn.run(self.app, host=self.host, port=self.port, log_level=self.log_level)
