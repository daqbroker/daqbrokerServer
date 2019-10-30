from daqbrokerServer.web.routes.auth import app as auth
from daqbrokerServer.web.routes.users import app as users
from daqbrokerServer.web.routes.connections import app as connections

routes = {}

routes["auth"] = auth
routes["users"] = users
routes["connections"] = connections