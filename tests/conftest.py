import os
import sys
import tempfile

# Configura el entorno ANTES de importar la app, para no depender del .env real.
os.environ["JWT_SECRET_KEY"] = "clave-de-prueba"
os.environ["APP_USERS"] = '{"admin": "password123"}'
os.environ["FLASK_DEBUG"] = "false"
os.environ["RATELIMIT_STORAGE_URI"] = "memory://"

# Base de datos temporal aislada para los tests
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["DATABASE_URL"] = "sqlite:///" + _db_path.replace("\\", "/")

# La app importa sus módulos como paquetes de nivel superior (routes.*),
# así que añadimos src/ al path igual que hace run.py.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, ROOT)

import pytest
from src.app import app as flask_app, limiter

# Desactivamos el rate limiter para que no interfiera entre tests
# (self.enabled se lee en cada request, así que basta con el atributo)
limiter.enabled = False


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def auth_header(client):
    resp = client.post("/login", json={"username": "admin", "password": "password123"})
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
