<#
  scripts/setup_dev.ps1
  Script de ayuda para configurar un entorno de desarrollo en Windows (PowerShell).
  Ejecutar desde la raíz del proyecto: .\scripts\setup_dev.ps1
#>

param(
    [switch]$Populate
)

Write-Host "Iniciando setup de desarrollo..." -ForegroundColor Cyan

if (-Not (Test-Path -Path .\.venv)) {
    python -m venv .venv
}

Write-Host "Activando entorno virtual .venv" -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

Write-Host "Actualizando pip e instalando dependencias" -ForegroundColor Cyan
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt

Write-Host "Instalando hooks pre-commit" -ForegroundColor Cyan
pre-commit install

Write-Host "Aplicando migraciones" -ForegroundColor Cyan
python manage.py makemigrations
python manage.py migrate

if ($Populate) {
    Write-Host "Poblando BD con datos de ejemplo" -ForegroundColor Cyan
    python -c "from utils.db_populate import populate_mangas; populate_mangas()"
}

Write-Host "Listo. Para ejecutar el servidor: python manage.py runserver" -ForegroundColor Green

