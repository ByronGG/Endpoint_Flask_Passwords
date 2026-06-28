"""Test de integración del cargado de configuración desde un archivo .env real.

A diferencia de test_app.py (que define las variables en os.environ ANTES de
importar la app), este test arranca la app en un subproceso con un entorno
LIMPIO y un archivo .env de verdad. Así depende de que `load_dotenv()` se
ejecute en el momento correcto.

Atrapa el bug de orden de inicialización: si `load_dotenv()` corre DESPUÉS de
importar los blueprints, `USERS_DB` se construye con APP_USERS vacío y todo
login devuelve 401, aunque los tests in-process sigan pasando.
"""

import os
import sys
import subprocess
import textwrap

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# Variables que la app debe tomar del .env, no del entorno heredado
_ENV_KEYS = ("JWT_SECRET_KEY", "APP_USERS", "DATABASE_URL", "RATELIMIT_STORAGE_URI", "FLASK_DEBUG")


def _run_app_with_env_file(env_dir):
    """Importa la app y prueba un login en un subproceso cuyo cwd es env_dir
    (donde vive el .env) y con un entorno sin las variables de auth."""
    script = textwrap.dedent(
        """
        from src.app import app
        client = app.test_client()
        resp = client.post("/login", json={"username": "tester", "password": "clave-tester"})
        assert resp.status_code == 200, f"login status {resp.status_code}: {resp.get_json()}"
        print("LOGIN_OK")
        """
    )

    # Entorno limpio: quitamos las variables de auth para forzar la lectura del .env
    env = {k: v for k, v in os.environ.items() if k not in _ENV_KEYS}
    env["PYTHONPATH"] = os.pathsep.join([PROJECT_ROOT, SRC_DIR])

    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(env_dir),
        env=env,
        capture_output=True,
        text=True,
    )


def test_login_works_loading_credentials_from_env_file(tmp_path):
    db_path = (tmp_path / "test.db").as_posix()
    (tmp_path / ".env").write_text(
        "JWT_SECRET_KEY=secreto-de-prueba\n"
        'APP_USERS={"tester": "clave-tester"}\n'
        f"DATABASE_URL=sqlite:///{db_path}\n"
        "RATELIMIT_STORAGE_URI=memory://\n"
        "FLASK_DEBUG=false\n",
        encoding="utf-8",
    )

    result = _run_app_with_env_file(tmp_path)

    assert result.returncode == 0, (
        "La app no cargó las credenciales del .env (posible bug de orden en "
        "load_dotenv()).\n--- stdout ---\n" + result.stdout +
        "\n--- stderr ---\n" + result.stderr
    )
    assert "LOGIN_OK" in result.stdout
