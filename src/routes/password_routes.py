import secrets
import string
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

password_bp = Blueprint("password", __name__)

@password_bp.route("/generate-password", methods=["GET"])
@jwt_required()
def generate_password():
    try:
        length = int(request.args.get("length", 12))
        use_special = request.args.get("special_chars", "true").lower() == "true"
        use_numbers = request.args.get("numbers", "true").lower() == "true"
        use_uppercase = request.args.get("uppercase", "true").lower() == "true"

        if length < 8 or length > 128:
            return jsonify({"error": "La longitud debe estar entre 8 y 128 caracteres"}), 400

        characters = string.ascii_lowercase
        if use_uppercase:
            characters += string.ascii_uppercase
        if use_numbers:
            characters += string.digits
        if use_special:
            characters += string.punctuation

        password = "".join(secrets.choice(characters) for _ in range(length))

        return jsonify({"password": password})

    except ValueError:
        return jsonify({"error": "El parámetro 'length' debe ser un número válido"}), 400
