from daqbroker.web.routes.auth import app as auth
from daqbroker.web.routes.users import app as users
from daqbroker.web.routes.connections import app as connections

routes = {}

routes["auth"] = auth
routes["users"] = users
routes["connections"] = connections