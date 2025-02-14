from flask import Flask
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from routes.password_routes import password_bp, init_limiter
from routes.auth_routes import auth_bp

app = Flask(__name__)

# Clave secreta para JWT
app.config["JWT_SECRET_KEY"] = "clave_super_secreta"
jwt = JWTManager(app)

# Configuración del rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Registrar los Blueprints
app.register_blueprint(init_limiter(limiter))
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)
