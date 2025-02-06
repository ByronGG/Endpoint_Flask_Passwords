from flask import Flask
from flask_jwt_extended import JWTManager
from routes.password_routes import password_bp
from routes.auth_routes import auth_bp

app = Flask(__name__)

# Clave secreta para JWT
app.config["JWT_SECRET_KEY"] = "clave_super_secreta"
jwt = JWTManager(app)

# Registrar los Blueprints
app.register_blueprint(password_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)
