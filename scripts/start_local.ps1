<#
.SYNOPSIS
    Usage: Open PowerShell and run: .\scripts\start_local.ps1
    Creates a virtual environment (.venv), installs requirements and starts the app.
#>

param(
    [string]$VenvPath = ".venv"
)

# Ajusta para a raiz do projeto (subindo um nível de 'scripts/')
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
Set-Location $root

if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtualenv at $VenvPath..."
    python -m venv $VenvPath
}

$Activate = Join-Path $VenvPath "Scripts/Activate.ps1"
if (Test-Path $Activate) {
    . $Activate
}

python -m pip install --upgrade pip

# Instala os requirements apontando para a pasta correta
if (Test-Path "Server/requirements.txt") {
    python -m pip install -r Server/requirements.txt
} else {
    Write-Host "Error: Server/requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# Load .env into process environment
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^[\s#]*$') { return }
        if ($_ -match '^\s*#') { return }
        $parts = $_ -split '=', 2
        if ($parts.Count -eq 2) {
            $name = $parts[0].Trim()
            $value = $parts[1].Trim()
            [System.Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
}

# Start server: usa Waitress (se instalado) ou Flask dev server (ideal para Windows)
Set-Location "Server"
if (Get-Command waitress-serve -ErrorAction SilentlyContinue) {
    waitress-serve --host=0.0.0.0 --port=8080 wsgi:app
} else {
    $env:FLASK_APP = "main.py"
    python -m flask run --host=0.0.0.0 --port=8080
}