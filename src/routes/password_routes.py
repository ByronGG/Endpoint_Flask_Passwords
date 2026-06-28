import secrets
import string
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, PasswordHistory

password_bp = Blueprint("password", __name__)


def init_limiter(limiter):
    @password_bp.route("/generate-password", methods=["GET"])
    @limiter.limit("10 per minute")
    @jwt_required()
    def generate_password():
        try:
            length = int(request.args.get("length", 12))
        except ValueError:
            return jsonify({"error": "El parámetro 'length' debe ser un número válido"}), 400

        use_special = request.args.get("special_chars", "true").lower() == "true"
        use_numbers = request.args.get("numbers", "true").lower() == "true"
        use_uppercase = request.args.get("uppercase", "true").lower() == "true"

        if length < 8 or length > 128:
            return jsonify({"error": "La longitud debe estar entre 8 y 128 caracteres"}), 400

        # Construimos los conjuntos de caracteres según las opciones solicitadas.
        # Las minúsculas siempre están presentes como base.
        pools = [string.ascii_lowercase]
        if use_uppercase:
            pools.append(string.ascii_uppercase)
        if use_numbers:
            pools.append(string.digits)
        if use_special:
            pools.append(string.punctuation)

        # Garantizamos al menos un carácter de cada tipo habilitado.
        # Al construir la contraseña así, siempre cumple los requisitos y no
        # hace falta regenerarla recursivamente.
        password_chars = [secrets.choice(pool) for pool in pools]

        all_characters = "".join(pools)
        password_chars += [secrets.choice(all_characters) for _ in range(length - len(password_chars))]

        secrets.SystemRandom().shuffle(password_chars)
        password = "".join(password_chars)

        # Guardamos solo los metadatos en el historial (nunca la contraseña)
        entry = PasswordHistory(
            username=get_jwt_identity(),
            length=len(password),
            has_special=use_special,
            has_numbers=use_numbers,
            has_uppercase=use_uppercase,
        )
        db.session.add(entry)
        db.session.commit()

        return jsonify({
            "password": password,
            "length": len(password),
            "contains_lowercase": True,
            "contains_uppercase": use_uppercase,
            "contains_numbers": use_numbers,
            "contains_special": use_special,
        })

    return password_bp


@password_bp.route("/password-history", methods=["GET"])
@jwt_required()
def get_password_history():
    username = get_jwt_identity()
    entries = (
        PasswordHistory.query
        .filter_by(username=username)
        .order_by(PasswordHistory.created_at.desc())
        .limit(50)
        .all()
    )
    return jsonify({"history": [entry.to_dict() for entry in entries]})


@password_bp.route("/check-password-strength", methods=["POST"])
@jwt_required()
def check_password_strength():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data.get("password"):
        return jsonify({"error": "Se requiere el campo 'password'"}), 400

    password = data["password"]

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
        "rating": ["Muy débil", "Débil", "Moderada", "Fuerte", "Muy fuerte"][min(max(score - 1, 0), 4)]
    })
