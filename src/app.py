import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from models import db
from routes.password_routes import password_bp, init_limiter
from routes.auth_routes import auth_bp

# Carga las variables definidas en el archivo .env (si existe)
load_dotenv()

app = Flask(__name__)

# Clave secreta para JWT (obligatoria, sin valor por defecto inseguro)
jwt_secret = os.environ.get("JWT_SECRET_KEY")
if not jwt_secret:
    raise RuntimeError(
        "Falta JWT_SECRET_KEY. Define la variable en el archivo .env "
        "(usa .env.example como plantilla)."
    )
app.config["JWT_SECRET_KEY"] = jwt_secret

# Base de datos (SQLite por defecto; configurable con DATABASE_URL)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///history.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
jwt = JWTManager(app)

# Configuración del rate limiter. El almacenamiento es configurable:
# memory:// para desarrollo, redis://host:puerto para producción.
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
)

# Registrar los Blueprints
app.register_blueprint(init_limiter(limiter))
app.register_blueprint(auth_bp)

# Crear las tablas si no existen
with app.app_context():
    db.create_all()
