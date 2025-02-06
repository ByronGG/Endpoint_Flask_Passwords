from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint("auth", __name__)

# Base de datos simulada de usuarios
USERS_DB = {
    "admin": "password123", # Cambiar a credenciales reales xd
    "usuario1": "claveSegura"
}

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in USERS_DB and USERS_DB[username] == password:
        expires = datetime.timedelta(hours=1)  # Token válido por 1 hora
        access_token = create_access_token(identity=username, expires_delta=expires)
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Credenciales incorrectas"}), 401
