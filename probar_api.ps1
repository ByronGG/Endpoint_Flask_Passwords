# =============================================================================
#  probar_api.ps1 - Script de prueba para la API de generacion de contraseñas
# =============================================================================
#  Uso:
#    1. Arranca el servidor en otra ventana:  python run.py
#    2. Ejecuta este script:                  .\probar_api.ps1
#
#  Parametros opcionales:
#    -BaseUrl   URL del servidor   (por defecto http://127.0.0.1:5000)
#    -Username  Usuario para login (por defecto admin)
#    -Password  Contraseña         (por defecto password123)
# =============================================================================

param(
    [string]$BaseUrl  = "http://127.0.0.1:5000",
    [string]$Username = "admin",
    [string]$Password = "password123"
)

$ErrorActionPreference = "Stop"

# --- Funciones auxiliares para imprimir con colores ---------------------------
function Write-Titulo($texto) {
    Write-Host ""
    Write-Host "=== $texto ===" -ForegroundColor Cyan
}
function Write-Ok($texto)   { Write-Host "  [OK]   $texto" -ForegroundColor Green }
function Write-Falla($texto){ Write-Host "  [X]    $texto" -ForegroundColor Red }
function Write-Info($texto) { Write-Host "  $texto" -ForegroundColor Gray }

# Llama a la API y devuelve un objeto con el status y el cuerpo, sin que un
# 4xx/5xx detenga el script (asi podemos probar tambien los casos de error).
function Invoke-Api {
    param(
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        [string]$Body
    )
    try {
        $params = @{
            Method      = $Method
            Uri         = $Url
            Headers     = $Headers
            ContentType = "application/json"
        }
        if ($Body) { $params["Body"] = $Body }
        $resp = Invoke-WebRequest @params
        return @{ Status = [int]$resp.StatusCode; Body = ($resp.Content | ConvertFrom-Json) }
    }
    catch {
        $status = -1
        $body   = $null
        if ($_.Exception.Response) {
            try { $status = [int]$_.Exception.Response.StatusCode } catch {}
        }
        # El cuerpo del error: en PowerShell 7 viene en ErrorDetails.Message
        if ($_.ErrorDetails -and $_.ErrorDetails.Message) {
            try { $body = $_.ErrorDetails.Message | ConvertFrom-Json }
            catch { $body = $_.ErrorDetails.Message }
        }
        return @{ Status = $status; Body = $body }
    }
}

Write-Host "Probando la API en $BaseUrl" -ForegroundColor Yellow

# Verificamos que el servidor responda antes de empezar
try {
    Invoke-WebRequest -Uri $BaseUrl -Method Get -TimeoutSec 3 | Out-Null
} catch {
    if (-not $_.Exception.Response) {
        Write-Falla "No se pudo conectar a $BaseUrl. Arranca el servidor con 'python run.py'."
        exit 1
    }
}

# -----------------------------------------------------------------------------
# 1. LOGIN
# -----------------------------------------------------------------------------
Write-Titulo "1. Login (obtener token JWT)"
$loginBody = @{ username = $Username; password = $Password } | ConvertTo-Json
$login = Invoke-Api -Method Post -Url "$BaseUrl/login" -Body $loginBody

if ($login.Status -ne 200) {
    Write-Falla "Login fallido (status $($login.Status)). Revisa usuario/contraseña en .env."
    exit 1
}
$token   = $login.Body.access_token
$headers = @{ Authorization = "Bearer $token" }
Write-Ok "Login correcto. Token: $($token.Substring(0,20))..."

# -----------------------------------------------------------------------------
# 2. GENERAR CONTRASEÑAS
# -----------------------------------------------------------------------------
Write-Titulo "2. Generar contraseñas"

$r = Invoke-Api -Method Get -Url "$BaseUrl/generate-password" -Headers $headers
Write-Ok "Por defecto (longitud $($r.Body.length)): $($r.Body.password)"

$r = Invoke-Api -Method Get -Url "$BaseUrl/generate-password?length=24" -Headers $headers
Write-Ok "Longitud 24: $($r.Body.password)"

$r = Invoke-Api -Method Get -Url "$BaseUrl/generate-password?length=16&special_chars=false&numbers=false" -Headers $headers
Write-Ok "Solo letras (16): $($r.Body.password)"
Write-Info "contains_special=$($r.Body.contains_special)  contains_numbers=$($r.Body.contains_numbers)"

# -----------------------------------------------------------------------------
# 3. HISTORIAL (persistencia en base de datos)
# -----------------------------------------------------------------------------
Write-Titulo "3. Historial de contraseñas generadas"
$r = Invoke-Api -Method Get -Url "$BaseUrl/password-history" -Headers $headers
Write-Ok "Entradas en el historial: $($r.Body.history.Count)"
$r.Body.history | Select-Object -First 3 | ForEach-Object {
    Write-Info "fecha=$($_.date)  longitud=$($_.length)  especiales=$($_.has_special)"
}

# -----------------------------------------------------------------------------
# 4. FORTALEZA DE UNA CONTRASEÑA
# -----------------------------------------------------------------------------
Write-Titulo "4. Evaluar fortaleza"
foreach ($pwd in @("123", "Abc123!seguraXYZ")) {
    $body = @{ password = $pwd } | ConvertTo-Json
    $r = Invoke-Api -Method Post -Url "$BaseUrl/check-password-strength" -Headers $headers -Body $body
    Write-Ok "'$pwd' -> fuerza $($r.Body.strength)/5 ($($r.Body.rating))"
}

# -----------------------------------------------------------------------------
# 5. CASOS DE ERROR (deben fallar a proposito)
# -----------------------------------------------------------------------------
Write-Titulo "5. Casos de error esperados"

$r = Invoke-Api -Method Post -Url "$BaseUrl/login" -Body (@{ username = "admin"; password = "mala" } | ConvertTo-Json)
if ($r.Status -eq 401) { Write-Ok "Login con contraseña incorrecta -> 401 (correcto)" }
else { Write-Falla "Se esperaba 401, se obtuvo $($r.Status)" }

$r = Invoke-Api -Method Get -Url "$BaseUrl/generate-password"
if ($r.Status -eq 401) { Write-Ok "Generar sin token -> 401 (correcto)" }
else { Write-Falla "Se esperaba 401, se obtuvo $($r.Status)" }

$r = Invoke-Api -Method Get -Url "$BaseUrl/generate-password?length=4" -Headers $headers
if ($r.Status -eq 400) { Write-Ok "Longitud fuera de rango (4) -> 400 (correcto)" }
else { Write-Falla "Se esperaba 400, se obtuvo $($r.Status)" }

$r = Invoke-Api -Method Get -Url "$BaseUrl/generate-password?length=abc" -Headers $headers
if ($r.Status -eq 400) { Write-Ok "Longitud no numerica (abc) -> 400 (correcto)" }
else { Write-Falla "Se esperaba 400, se obtuvo $($r.Status)" }

Write-Host ""
Write-Host "Pruebas finalizadas." -ForegroundColor Yellow
Write-Host "Nota: si generas mas de 10 contraseñas por minuto veras un 429 (rate limit)." -ForegroundColor DarkGray
