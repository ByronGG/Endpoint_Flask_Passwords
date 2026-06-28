import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from src.app import app

if __name__ == "__main__":
    # El modo debug solo se activa si FLASK_DEBUG=true en el .env (apagado por defecto)
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)
