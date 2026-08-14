<#
Usage: Open PowerShell and run: .\scripts\start_local.ps1
Creates a virtual environment (.venv), installs requirements and starts the app.
If gunicorn is present it will be used; otherwise Flask dev server is used.
#>

git config user.name "Victor-Alex-Moreira-Gouveia"
git config user.email "victor.alex.moreira.gouveia@gmail.com"

param(
    [string]$VenvPath = ".venv"
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtualenv at $VenvPath..."
    python -m venv $VenvPath
}

$Activate = Join-Path $VenvPath "Scripts/Activate.ps1"
if (Test-Path $Activate) {
    & $Activate
}

python -m pip install --upgrade pip
python -m pip install -r Server/requirements.txt

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

# Start server: prefer gunicorn if available
if (Get-Command gunicorn -ErrorAction SilentlyContinue) {
    Set-Location "Server"
    gunicorn --bind 0.0.0.0:8080 wsgi:app
} else {
    $env:FLASK_APP = "Server.main"
    python -m flask run --host=0.0.0.0 --port=8080
}
