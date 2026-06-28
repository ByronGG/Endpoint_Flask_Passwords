import os
import json
import datetime
import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)


def _load_users():
    """Lee los usuarios desde la variable de entorno APP_USERS y devuelve un
    diccionario {usuario: hash bcrypt}. Las contraseñas nunca se guardan en
    texto plano en memoria: se hashean con bcrypt al iniciar la aplicación."""
    raw = os.environ.get("APP_USERS", "{}")
    try:
        plain_users = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "APP_USERS no es un JSON válido. Usa el formato "
            '{"usuario": "contraseña"} en el archivo .env.'
        ) from exc
    return {
        user: bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
        for user, pwd in plain_users.items()
    }


# Diccionario {usuario: hash} cargado una sola vez al importar el módulo
USERS_DB = _load_users()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Se requiere un cuerpo JSON válido"}), 400

    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Se requieren los campos 'username' y 'password'"}), 400

    stored_hash = USERS_DB.get(username)
    # bcrypt trunca silenciosamente a 72 bytes; el encode es necesario para checkpw
    if stored_hash and bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        expires = datetime.timedelta(hours=1)  # Token válido por 1 hora
        access_token = create_access_token(identity=username, expires_delta=expires)
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Credenciales incorrectas"}), 401
