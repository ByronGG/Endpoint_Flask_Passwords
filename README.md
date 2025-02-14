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

- **Generación de contraseñas seguras**: Genera contraseñas de longitud personalizada.
- **Autenticación**: Uso de tokens JWT para proteger los endpoints.
- **Límites**: Se establece una longitud máxima de 128 caracteres para las contraseñas generadas.


## Requisitos

- Python 3.8+
- Flask
- Flask-JWT-Extended

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

## Uso de la Endpoint
1. Ejecuta la aplicación Flask:
```bash
python run.py
```
2. La aplicación estará por defecto en el puerto http://127.0.0.1:5000.
3. Puedes realizar peticiones usando herramientas como Postman o cURL.

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
Genera un contraseña segura con longitud personalizada.
Parámetros de consulta:
- **length:** (opcional) Longitud de la contraseña a generar (minimo 8 hasta un máximo 128 caracteres).
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
## Códigos de Error:
- 400: Parámetros inválidos (por ejemplo, longitud fuera de rango)
- 401: No autorizado (token inválido o expirado)
- 429: Demasiadas peticiones (rate limit excedido)

## Contribuciones
Las contribuciones son bienvenidas, este es un pequeño proyecto de un desarrollador Jr. que acaba de empezar su trayectoria 🙂.
