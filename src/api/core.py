from auth.main import app as auth_app
from catalogo.main import app as catalogo_app
from common.app import create_app

from api._compose import include_domain_routes


app = create_app("Duality Core API")
include_domain_routes(app, auth_app, catalogo_app)
