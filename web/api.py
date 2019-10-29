from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket

from daqbroker.web.routes import routes
from daqbroker.web.socket.notifier import Notifier

api = APIRouter()

notifier = Notifier(subjects = {})

for route_name, route_obj in routes.items():
	api.include_router(
		route_obj,
		prefix="/" + route_name,
		tags=[route_name],
		responses={404: {"description": "Not found"}}
	)

@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await notifier.connect(websocket)
	try:
		while True:
			data = await websocket.receive_text()
			await websocket.send_text(f"Message text was: {data}")
	except WebSocketDisconnect:
		notifier.remove(websocket)