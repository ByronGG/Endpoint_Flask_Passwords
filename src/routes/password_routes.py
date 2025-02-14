import secrets
import string
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import unittest

password_bp = Blueprint("password", __name__)

def init_limiter(limiter):
    @password_bp.route("/generate-password", methods=["GET"])
    @limiter.limit("10 per minute")
    @jwt_required()
    def generate_password():
        try:
            length = int(request.args.get("length", 12))
            use_special = request.args.get("special_chars", "true").lower() == "true"
            use_numbers = request.args.get("numbers", "true").lower() == "true"
            use_uppercase = request.args.get("uppercase", "true").lower() == "true"

            if length < 8 or length > 128:
                return jsonify({"error": "La longitud debe estar entre 8 y 128 caracteres"}), 400

            # Aseguramos que todos los tipos de caracteres estén habilitados
            use_special = True
            use_numbers = True
            use_uppercase = True

            # Construimos el conjunto de caracteres
            characters = string.ascii_lowercase
            characters += string.ascii_uppercase
            characters += string.digits
            characters += string.punctuation

            # Generamos la contraseña inicial
            password = []
            
            # Aseguramos al menos un carácter de cada tipo
            password.append(secrets.choice(string.ascii_lowercase))
            password.append(secrets.choice(string.ascii_uppercase))
            password.append(secrets.choice(string.digits))
            password.append(secrets.choice(string.punctuation))

            # Completamos el resto de la contraseña
            for _ in range(length - 4):
                password.append(secrets.choice(characters))

            # Mezclamos los caracteres
            password = list(password)
            secrets.SystemRandom().shuffle(password)
            password = ''.join(password)

            # Validamos que la contraseña cumple con todos los requisitos
            if not all([
                any(c.islower() for c in password),
                any(c.isupper() for c in password),
                any(c.isdigit() for c in password),
                any(c in string.punctuation for c in password)
            ]):
                # Si no cumple, generamos otra
                return generate_password()

            return jsonify({
                "password": password,
                "length": len(password),
                "contains_lowercase": True,
                "contains_uppercase": True,
                "contains_numbers": True,
                "contains_special": True
            })

        except ValueError:
            return jsonify({"error": "El parámetro 'length' debe ser un número válido"}), 400

    return password_bp

@password_bp.route("/password-history", methods=["GET"])
@jwt_required()
def get_password_history():
    # Aquí implementarías la lógica de base de datos
    # Este es solo un ejemplo conceptual
    return jsonify({
        "history": [
            {
                "date": datetime.now().isoformat(),
                "length": 12,
                "has_special": True
            }
        ]
    })

@password_bp.route("/check-password-strength", methods=["POST"])
@jwt_required()
def check_password_strength():
    data = request.get_json()
    password = data.get("password")
    
    score = 0
    feedback = []
    
    if len(password) >= 12:
        score += 1
        feedback.append("Longitud adecuada")
    if any(c.isupper() for c in password):
        score += 1
        feedback.append("Contiene mayúsculas")
    if any(c.islower() for c in password):
        score += 1
        feedback.append("Contiene minúsculas")
    if any(c.isdigit() for c in password):
        score += 1
        feedback.append("Contiene números")
    if any(c in string.punctuation for c in password):
        score += 1
        feedback.append("Contiene caracteres especiales")
        
    return jsonify({
        "strength": score,
        "feedback": feedback,
        "rating": ["Muy débil", "Débil", "Moderada", "Fuerte", "Muy fuerte"][min(score-1, 4)]
    })

class PasswordGeneratorTests(unittest.TestCase):
    def test_password_length(self):
        # Implementar tests
        pass
    
    def test_password_complexity(self):
        # Implementar tests
        pass
