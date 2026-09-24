# Django Backend Deployment Script for Windows
# Run this script to deploy the Django backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Django Backend Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "Python not found. Please install Python 3.9 or later." -ForegroundColor Red
    exit 1
}

# Navigate to backend directory
Write-Host "Navigating to backend directory..." -ForegroundColor Yellow
Set-Location backend\Django

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Cyan
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "Failed to install dependencies." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env file with your configuration." -ForegroundColor Cyan
    Write-Host "Press Enter to continue after editing .env file..."
    Read-Host
}

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
python manage.py migrate
if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrations completed successfully." -ForegroundColor Green
} else {
    Write-Host "Migration failed. Please check your database configuration." -ForegroundColor Red
    exit 1
}

# Collect static files
Write-Host "Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput
if ($LASTEXITCODE -eq 0) {
    Write-Host "Static files collected successfully." -ForegroundColor Green
} else {
    Write-Host "Failed to collect static files." -ForegroundColor Red
}

# Create superuser (optional)
Write-Host "Do you want to create a superuser? (y/n)" -ForegroundColor Yellow
$createSuperuser = Read-Host
if ($createSuperuser -eq 'y' -or $createSuperuser -eq 'Y') {
    python manage.py createsuperuser
}

# Start development server
Write-Host "Starting Django development server..." -ForegroundColor Green
Write-Host "Server will be available at http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Cyan
Write-Host ""

python manage.py runserver
