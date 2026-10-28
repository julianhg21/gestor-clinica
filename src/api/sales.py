from common.app import create_app
from pagos.main import app as pagos_app
from pedidos.main import app as pedidos_app

from api._compose import include_domain_routes


app = create_app("Duality Sales API")
include_domain_routes(app, pedidos_app, pagos_app)
