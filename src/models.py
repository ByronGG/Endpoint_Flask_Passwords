from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _utcnow():
    return datetime.now(timezone.utc)


class PasswordHistory(db.Model):
    """Registro de metadatos de cada contraseña generada.

    Por seguridad NO se guarda la contraseña en sí, solo sus características."""

    __tablename__ = "password_history"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=_utcnow, nullable=False)
    length = db.Column(db.Integer, nullable=False)
    has_special = db.Column(db.Boolean, nullable=False)
    has_numbers = db.Column(db.Boolean, nullable=False)
    has_uppercase = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            "date": self.created_at.isoformat(),
            "length": self.length,
            "has_special": self.has_special,
            "has_numbers": self.has_numbers,
            "has_uppercase": self.has_uppercase,
        }
