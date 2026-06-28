# Endpoint Flask Password Generator 

<h3 align="left">Lenguajes y Herramientas:</h3>
<p align="left"> 
  <a href="https://flask.palletsprojects.com/" target="_blank" rel="noreferrer"> 
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Flask_logo.svg/2560px-Flask_logo.svg.png" alt="flask" width="40" height="40"/> 
  </a> 
  <a href="https://postman.com" target="_blank" rel="noreferrer"> 
    <img src="https://www.vectorlogo.zone/logos/getpostman/getpostman-icon.svg" alt="postman" width="40" height="40"/> 
  </a> 
  <a href="https://www.python.org" target="_blank" rel="noreferrer"> 
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> 
  </a> 
</p>


Este proyecto es una API RESTful creada con Flask para generar contraseñas seguras y realizar autenticación utilizando tokens JWT. La API permite la generación de contraseñas personalizadas y protegidas por autenticación.

## Funcionalidades

- **Generación de contraseñas seguras**: Genera contraseñas de longitud personalizada (8 a 128) usando el módulo `secrets`.
- **Autenticación**: Uso de tokens JWT para proteger los endpoints. Las contraseñas de los usuarios se almacenan **hasheadas con bcrypt**.
- **Historial persistente**: Cada contraseña generada se registra en una base de datos (SQLite por defecto) — solo metadatos, nunca la contraseña.
- **Evaluación de fortaleza**: Endpoint para puntuar qué tan fuerte es una contraseña.
- **Rate limiting**: Límites por IP (configurable con almacenamiento en memoria o Redis).
- **Configuración por entorno**: Los secretos y usuarios se leen de un archivo `.env` (no se suben a git).


## Requisitos

- Python 3.8+ (probado en 3.14)
- Flask, Flask-JWT-Extended, Flask-Limiter, Flask-SQLAlchemy
- bcrypt, python-dotenv
- Redis (opcional, solo para el rate limiter en producción)

Todas las dependencias están en `requirements.txt`.

## Instalación

### Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/Endpoint_Flask_Passwords.git
cd Endpoint_Flask_Passwords
```

## Entorno Virtual (Opcional pero recomendado)

En windows
```bash
.\venv\Scripts\activate
```

En macOs/Linux
```bash
source venv/bin/activate
```

Instalar las dependecias necesarias
```bash
pip install -r requirements.txt
```

## Configuración (.env)

La aplicación lee su configuración de un archivo `.env`. Copia la plantilla y rellena los valores:

```bash
cp .env.example .env
```

Variables disponibles:

| Variable | Descripción | Por defecto |
|----------|-------------|-------------|
| `JWT_SECRET_KEY` | Clave para firmar los tokens JWT (**obligatoria**). Genérala con `python -c "import secrets; print(secrets.token_urlsafe(48))"` | — |
| `APP_USERS` | Usuarios en formato JSON: `{"admin": "password123"}` | `{}` |
| `DATABASE_URL` | URL de la base de datos (SQLAlchemy) | `sqlite:///history.db` |
| `RATELIMIT_STORAGE_URI` | Almacenamiento del rate limiter (`memory://` o `redis://host:puerto`) | `memory://` |
| `FLASK_DEBUG` | `true` activa el modo debug (solo desarrollo) | `false` |

> El `.env` está en `.gitignore` y nunca debe subirse al repositorio.

## Uso de la Endpoint
1. Ejecuta la aplicación Flask:
```bash
python run.py
```
2. La aplicación estará por defecto en el puerto http://127.0.0.1:5000.
3. Puedes realizar peticiones usando herramientas como Postman o cURL.

### Script de prueba (Windows / PowerShell)

El repositorio incluye `probar_api.ps1`, que recorre todos los endpoints (login, generación, historial, fortaleza y casos de error). Con el servidor corriendo en otra ventana:

```powershell
.\probar_api.ps1
```

### Tests

```bash
pytest
```

## Endpoints
POST /login
Autenticación con nombre de usuario y contraseña para obtener token JWT.
Ejemplo de solicitud:
```json
{
  "username": "admin",
  "password": "password123"
}
```

Respuesta esperada en el body-json
```json
{
  "access_token": "tu_token_jwt_aqui"
}
```

GET /generate-password
Genera un contraseña segura con longitud personalizada. **Requiere token JWT.**
Parámetros de consulta:
- **length:** (opcional) Longitud de la contraseña a generar (mínimo 8 hasta un máximo 128 caracteres). Por defecto 12.
- **uppercase / numbers / special_chars:** (opcionales) `true`/`false` para incluir mayúsculas, números o caracteres especiales. Por defecto `true`. Las minúsculas siempre se incluyen.

Cada generación queda registrada en el historial.
Ejemplo de solicitud:

```bash
GET http://127.0.0.1:5000/generate-password?length=16
Headers "Authorization: Bearer tu_token_jwt_aqui"
```
Respuesta esperada:
```json
{
    "contains_lowercase": true,
    "contains_numbers": true,
    "contains_special": true,
    "contains_uppercase": true,
    "length": 12,
    "password": "{1i;m;Wz=//U"
}
```

GET /password-history
Devuelve las últimas 50 contraseñas generadas por el usuario autenticado (solo metadatos, nunca la contraseña). **Requiere token JWT.**
Respuesta esperada:
```json
{
    "history": [
        {
            "date": "2026-06-28T07:06:25.123456+00:00",
            "length": 16,
            "has_special": true,
            "has_numbers": true,
            "has_uppercase": true
        }
    ]
}
```

POST /check-password-strength
Evalúa la fortaleza de una contraseña dada. **Requiere token JWT.**
Ejemplo de solicitud:
```json
{
  "password": "Abc123!seguraXYZ"
}
```
Respuesta esperada:
```json
{
    "strength": 5,
    "rating": "Muy fuerte",
    "feedback": ["Longitud adecuada", "Contiene mayúsculas", "Contiene minúsculas", "Contiene números", "Contiene caracteres especiales"]
}
```

## Caracteristicas de seguridad implementadas
Rate Limiting:
- 200 peticiones por día
- 50 peticiones por hora
- 10 peticiones por minuto para la generación de contraseñas
## Validaciones de Contraseña:
- Mínimo 8 caracteres
- Máximo 128 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número
- Al menos un carácter especial
## Seguridad JWT:
- Los tokens expiran después de 1 hora
- Todas las peticiones de generación de contraseñas requieren autenticación
## Almacenamiento de credenciales:
- Las contraseñas de los usuarios se hashean con bcrypt al iniciar la aplicación
- El secreto JWT y los usuarios se cargan desde el `.env` (nunca hardcodeados en el código)
## Códigos de Error:
- 400: Parámetros inválidos (por ejemplo, longitud fuera de rango)
- 401: No autorizado (token inválido o expirado)
- 429: Demasiadas peticiones (rate limit excedido)

## Contribuciones
Las contribuciones son bienvenidas, este es un pequeño proyecto de un desarrollador Jr. que acaba de empezar su trayectoria 🙂.
